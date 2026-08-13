"""Deterministic, token-driven PPTX projection of the strict v3 deck model."""
import argparse, json, math, os, sys, tempfile
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument("--spec",required=True); p.add_argument("--output",required=True); p.add_argument("--registry"); a=p.parse_args()
    try:
        from pptx import Presentation
        from pptx.chart.data import ChartData, XyChartData
        from pptx.dml.color import RGBColor
        from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_AXIS_CROSSES
        from pptx.enum.shapes import MSO_SHAPE
        from pptx.enum.text import PP_ALIGN
        from pptx.util import Inches, Pt
    except ImportError:
        print(json.dumps({"status":"unavailable","diagnostic":"python-pptx is not installed"})); return 3
    spec=json.loads(Path(a.spec).read_text(encoding="utf-8"))
    registry=Path(a.registry) if a.registry else Path(__file__).resolve().parents[1]/"design-systems"/"registry.json"
    systems=json.loads(registry.read_text(encoding="utf-8"))["systems"]
    token=next((x for x in systems if x["id"]==spec["design_system_id"]),None)
    if not token: print(json.dumps({"status":"failed","diagnostic":"unknown design system"})); return 2
    pal={k:RGBColor.from_string(v.lstrip("#")) for k,v in token["palette"].items()}
    head,body=token["fonts"]["heading"][0],token["fonts"]["body"][0]
    margin=token["grid"]["margin_in"]; gutter=token["grid"]["gutter_in"]; columns=token["grid"]["columns"]
    col=(13.333-2*margin-(columns-1)*gutter)/columns
    spacing=[x/72 for x in token["spacing_pt"]]
    prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
    prs.core_properties.title=spec["metadata"]["title"]; prs.core_properties.language=spec["metadata"]["language"]
    def tag(shape,name,alt=None):
        shape.name=name
        if alt is not None:
            nv=shape._element.xpath(".//p:cNvPr")[0]; nv.set("descr",alt)
        return shape
    def textbox(slide,name,text,x,y,w,h,size=None,bold=False,color=None,align=None,alt=None):
        sh=tag(slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)),name)
        tag(sh,name,str(text) if alt is None else alt)
        sh.text=text; tf=sh.text_frame; tf.word_wrap=True
        for para in tf.paragraphs:
            para.font.name=head if bold else body; para.font.size=Pt(size or token["type_pt"]["body"]); para.font.bold=bold; para.font.color.rgb=color or pal["text"]
            if align is not None: para.alignment=align
        return sh
    def grid_box(start,span,y,h):
        return margin+start*(col+gutter),y,span*col+(span-1)*gutter,h
    def add_cropped_picture(slide,path,x,y,w,h,focal):
        from PIL import Image
        with Image.open(path) as im: iw,ih=im.size
        sh=slide.shapes.add_picture(str(path),Inches(x),Inches(y),width=Inches(w),height=Inches(h))
        source_ratio=iw/ih; box_ratio=w/h
        fx,fy=.5,.5
        try:
            parts=[float(v.strip()) for v in focal.replace("%","").split(",")]
            fx,fy=(parts[0]/100,parts[1]/100) if max(parts)>1 else parts
        except Exception: pass
        if source_ratio>box_ratio:
            visible=box_ratio/source_ratio; left=max(0,min(1-visible,fx-visible/2)); sh.crop_left=left; sh.crop_right=1-visible-left
        else:
            visible=source_ratio/box_ratio; top=max(0,min(1-visible,fy-visible/2)); sh.crop_top=top; sh.crop_bottom=1-visible-top
        return sh
    def reorder(slide,order):
        by_name={x.name:x._element for x in slide.shapes}
        tree=slide.shapes._spTree
        for name in order:
            el=by_name.get(name)
            if el is not None: tree.remove(el); tree.append(el)
    def rect(slide,name,x,y,w,h,fill,alt=""):
        sh=tag(slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h)),name,alt or name)
        sh.fill.solid(); sh.fill.fore_color.rgb=fill; sh.line.fill.background(); return sh
    def semantic_colors(policy, count):
        base = {
            "categorical": [pal["accent"], pal["positive"], pal["warning"], pal["text"]],
            "sequential": [pal["accent"], pal["text"], pal["positive"], pal["warning"]],
            "diverging": [pal["warning"], pal["accent"], pal["positive"], pal["text"]],
            "status": [pal["positive"], pal["warning"], pal["text"], pal["accent"]],
        }[policy]
        return [base[i % len(base)] for i in range(count)]
    def chart_image(content, path):
        from PIL import Image, ImageDraw
        image=Image.new("RGB",(1305,578),tuple(pal["background"])); draw=ImageDraw.Draw(image)
        left,top,right,bottom=95,45,1250,510
        chart_type=content["chart_type"]
        rows=[[None if v is None else float(v) for v in s["values"]] for s in content["series"]]
        vals=[v for row in rows for v in row if v is not None] or [0]
        explicit=content.get("explicit_axis",{})
        ymin,ymax=(explicit.get("y_min"),explicit.get("y_max")) if content["axis_policy"]=="explicit" else (min(0,min(vals)),max(vals))
        if ymin is None: ymin,ymax=min(vals),max(vals)
        if ymax==ymin: ymax=ymin+1
        colors=semantic_colors(content["color_semantics"],len(rows))
        def py(v): return bottom-int((v-ymin)/(ymax-ymin)*(bottom-top))
        n=max(1,len(content["categories"]))
        if chart_type in ("pie","donut"):
            values=[max(0,v or 0) for v in rows[0]]
            total=sum(values)
            if total <= 0: raise ValueError(f"{chart_type} requires a positive part-to-whole total")
            box=(345,45,925,510); angle=-90
            slice_colors=semantic_colors(content["color_semantics"],len(values))
            for i,value in enumerate(values):
                end=angle+360*value/total
                draw.pieslice(box,start=angle,end=end,fill=tuple(slice_colors[i]),outline=tuple(pal["background"]),width=3)
                angle=end
            if chart_type=="donut":
                draw.ellipse((510,180,760,375),fill=tuple(pal["background"]))
        else:
            draw.line((left,bottom,right,bottom),fill=tuple(pal["text"]),width=3)
            draw.line((left,top,left,bottom),fill=tuple(pal["text"]),width=3)
        if chart_type=="column":
            group=(right-left)/n
            for si,row in enumerate(rows):
                for i,v in enumerate(row):
                    if v is None: continue
                    x0=left+i*group+group*(.12+si*.75/max(1,len(rows))); x1=x0+group*.65/max(1,len(rows))
                    draw.rectangle((x0,min(py(v),py(0)),x1,max(py(v),py(0))),fill=tuple(colors[si]))
        elif chart_type=="bar":
            group=(bottom-top)/n
            xmin=min(0,min(vals)); xmax=max(vals)
            if xmax==xmin: xmax=xmin+1
            px0=left+(0-xmin)/(xmax-xmin)*(right-left)
            for si,row in enumerate(rows):
                for i,v in enumerate(row):
                    if v is None: continue
                    y0=top+i*group+group*(.12+si*.75/max(1,len(rows))); y1=y0+group*.65/max(1,len(rows))
                    px=left+(v-xmin)/(xmax-xmin)*(right-left)
                    draw.rectangle((min(px0,px),y0,max(px0,px),y1),fill=tuple(colors[si]))
        elif chart_type=="scatter":
            xs=[float(x) for x in content["categories"]]
            xmin,xmax=(explicit.get("x_min"),explicit.get("x_max")) if content["axis_policy"]=="explicit" else (min(xs),max(xs))
            if xmax==xmin: xmax=xmin+1
            for si,row in enumerate(rows):
                for x,y in zip(xs,row):
                    if y is None: continue
                    px=left+(x-xmin)/(xmax-xmin)*(right-left); yy=py(y)
                    draw.ellipse((px-7,yy-7,px+7,yy+7),fill=tuple(colors[si]),outline=tuple(pal["text"]))
        elif chart_type in ("line","area"):
            for si,row in enumerate(rows):
                segments=[]; current=[]
                for i,v in enumerate(row):
                    if v is None:
                        if current: segments.append(current); current=[]
                        continue
                    current.append((left+(i+.5)*(right-left)/n,py(v)))
                if current: segments.append(current)
                for pts in segments:
                    if chart_type=="area" and len(pts)>1:
                        draw.polygon([(pts[0][0],py(0)),*pts,(pts[-1][0],py(0))],fill=tuple(colors[si]))
                    elif len(pts)>1:
                        draw.line(pts,fill=tuple(colors[si]),width=5)
                    for x,y in pts: draw.ellipse((x-5,y-5,x+5,y+5),fill=tuple(colors[si]))
        image.save(path,format="PNG",optimize=False)
    for s in spec["slides"]:
        if s["recipe"] != s["type"]:
            print(json.dumps({"status":"failed","diagnostic":f"recipe {s['recipe']} does not implement type {s['type']}"})); return 2
        slide=prs.slides.add_slide(prs.slide_layouts[6]); bg=slide.background.fill; bg.solid(); bg.fore_color.rgb=pal[s["background_role"]]
        dark_bg=s["background_role"]!="background"; fg=RGBColor(255,255,255) if dark_bg else pal["text"]; accent=RGBColor(255,255,255) if dark_bg else pal["accent"]
        title_y=.28 if s["layout_family"] in ("hero","visual") else .35
        textbox(slide,"title",s["title"],margin,title_y,13.333-2*margin,.72,token["type_pt"]["title"],True,fg,alt=s["title"])
        textbox(slide,"assertion",s["core_assertion"],margin,1.08,13.333-2*margin,.62,20,True,accent,alt=s["core_assertion"])
        c=s["content"]; typ=s["type"]
        if typ in ("title","section"):
            value=c.get("subtitle") or c.get("section_label") or s["implication"]
            textbox(slide,"visual",value,*grid_box(1,columns-2,2.15,2.2),30,False,fg,PP_ALIGN.CENTER,alt=s["accessibility"]["alt_text"])
        elif typ=="assertion-evidence":
            blocks=c["evidence_blocks"]; cols=max(1,len(blocks)); w=(13.333-2*margin-(cols-1)*gutter)/cols
            for i,b in enumerate(blocks):
                oid=b["object_id"]; sh=rect(slide,oid,margin+i*(w+gutter),2,w,2.9,pal["background"],b["text"])
                sh.text=b["text"]
                for para in sh.text_frame.paragraphs:
                    para.font.name=body; para.font.size=Pt(17); para.font.color.rgb=pal["text"]
        elif typ=="big-number":
            textbox(slide,"visual",f'{c["value"]} {c["unit"]}',*grid_box(1,columns-2,2,1.45),52,True,accent,PP_ALIGN.CENTER,alt=s["accessibility"]["alt_text"])
            textbox(slide,"content-1",c["context"],*grid_box(2,columns-4,3.65,1.1),19,False,fg,PP_ALIGN.CENTER)
        elif typ=="comparison":
            for i,(label,val) in enumerate((("Left",c["left"]),("Right",c["right"]))):
                sh=rect(slide,f"content-{i+1}",margin+i*6.05,2,5.75,3,pal["background"],str(val)); sh.text=str(val)
                for para in sh.text_frame.paragraphs:
                    para.font.name=body; para.font.size=Pt(17); para.font.color.rgb=pal["text"]
            textbox(slide,"comparison-basis",c["comparison_basis"],2,5.05,9.3,.45,13,True,pal["accent"],PP_ALIGN.CENTER)
        elif typ in ("process","timeline"):
            items=c["steps"] if typ=="process" else c["events"]; n=max(1,len(items)); w=11.8/n
            for i,item in enumerate(items):
                sh=rect(slide,item["object_id"],margin+i*w,2.25,w-.18,2.25,pal["accent"],str(item)); sh.text=str(item.get("label") or item.get("title") or item)
                for para in sh.text_frame.paragraphs:
                    para.font.name=body; para.font.size=Pt(15); para.font.bold=True; para.font.color.rgb=RGBColor(255,255,255); para.alignment=PP_ALIGN.CENTER
        elif typ=="chart":
            values=[]
            for series in c["series"]:
                row=[]
                for value in series["values"]:
                    if value is None and c["missing_value_policy"]=="zero": value=0
                    row.append(value)
                values.append(row)
            cmap={"bar":XL_CHART_TYPE.BAR_CLUSTERED,"column":XL_CHART_TYPE.COLUMN_CLUSTERED,"line":XL_CHART_TYPE.LINE_MARKERS,"area":XL_CHART_TYPE.AREA,"pie":XL_CHART_TYPE.PIE,"donut":XL_CHART_TYPE.DOUGHNUT,"scatter":XL_CHART_TYPE.XY_SCATTER}
            # Distribution and flow use the declared bar representation; correlation uses scatter.
            if c["relationship"]=="correlation" and c["chart_type"]!="scatter": raise ValueError("correlation requires scatter")
            if c["relationship"]=="flow" and c["chart_type"]!="bar": raise ValueError("flow requires bar")
            alt=f"{s['accessibility']['alt_text']}; color semantics: {c['color_semantics']}; non-color labels retained"
            if c["render_mode"]=="deterministic-image":
                with tempfile.NamedTemporaryFile(suffix=".png",delete=False) as image_file: image_path=Path(image_file.name)
                try:
                    chart_image(c,image_path)
                    chart_shape=slide.shapes.add_picture(str(image_path),Inches(margin),Inches(1.95),Inches(8.7),Inches(3.85))
                    tag(chart_shape,"chart",alt+"; deterministic image")
                finally:
                    image_path.unlink(missing_ok=True)
            else:
                if c["chart_type"]=="scatter":
                    data=XyChartData()
                    xs=[float(x) for x in c["categories"]]
                    for source,row in zip(c["series"],values):
                        series=data.add_series(source["name"])
                        for x,y in zip(xs,row):
                            if y is not None: series.add_data_point(x,y)
                else:
                    data=ChartData(); data.categories=c["categories"]
                    for source,row in zip(c["series"],values): data.add_series(source["name"],row)
                chart_shape=slide.shapes.add_chart(cmap[c["chart_type"]],Inches(margin),Inches(1.95),Inches(8.7),Inches(3.85),data)
                chart=chart_shape.chart; tag(chart_shape,"chart",alt+"; native editable")
                chart.has_legend=len(c["series"])>1
                if chart.has_legend: chart.legend.position=XL_LEGEND_POSITION.BOTTOM
                if c["chart_type"] not in ("pie","donut"):
                    chart.value_axis.has_title=True
                    explicit=c.get("explicit_axis",{})
                    chart.value_axis.axis_title.text_frame.text=explicit.get("y_title",c["units"])
                    if c["chart_type"]=="scatter":
                        chart.category_axis.has_title=True; chart.category_axis.axis_title.text_frame.text=explicit.get("x_title","X")
                    if c["axis_policy"]=="zero": chart.value_axis.minimum_scale=0
                    elif c["axis_policy"]=="log": chart.value_axis.log_base=10
                    elif c["axis_policy"]=="explicit":
                        chart.value_axis.minimum_scale=explicit["y_min"]; chart.value_axis.maximum_scale=explicit["y_max"]
                        if c["chart_type"]=="scatter":
                            chart.category_axis.minimum_scale=explicit["x_min"]; chart.category_axis.maximum_scale=explicit["x_max"]
                for i,series in enumerate(chart.series):
                    series.format.fill.solid(); series.format.fill.fore_color.rgb=semantic_colors(c["color_semantics"],len(chart.series))[i]
            textbox(slide,"content-annotation",c["annotation"],9.65,2.2,3.0,2.7,16,True,accent,alt=f"{c['focal_datum']}; {c['annotation']}; missing values: {c['missing_value_policy']}; colors: {c['color_semantics']}")
        elif typ=="image-led":
            image=Path(c["source"])
            if image.is_file():
                sh=add_cropped_picture(slide,image,margin,1.9,7.6,3.7,c["crop_focal_point"]); tag(sh,"image",c["alt_text"])
            else:
                sh=rect(slide,"image",margin,1.9,7.6,3.7,pal["accent"],c["alt_text"]); sh.text=c["fallback"]
                for para in sh.text_frame.paragraphs:
                    para.font.name=body; para.font.size=Pt(18); para.font.bold=True; para.font.color.rgb=RGBColor(255,255,255); para.alignment=PP_ALIGN.CENTER
            textbox(slide,"content-1",s["implication"],8.75,2.25,3.7,2.7,19,True)
        elif typ=="quote":
            textbox(slide,"quote","“"+c["quote"]+"”",1.1,2.0,11.1,2.15,28,False,pal["text"],PP_ALIGN.CENTER)
            textbox(slide,"content-attribution","— "+c["attribution"],6.5,4.35,5.2,.5,15,True,pal["accent"],PP_ALIGN.RIGHT)
        elif typ=="matrix":
            textbox(slide,"matrix","Matrix",5.4,1.82,2.4,.35,12,True,accent,PP_ALIGN.CENTER,alt=s["accessibility"]["alt_text"])
            textbox(slide,"matrix-x",c["x_axis"],4.2,5.45,5,.4,12,True,pal["accent"],PP_ALIGN.CENTER)
            textbox(slide,"matrix-y",c["y_axis"],.7,3.3,1.2,.6,12,True,pal["accent"],PP_ALIGN.CENTER)
            for item in c["items"]:
                x=2.1+item["x"]*7.65; y=5.05-item["y"]*2.65
                textbox(slide,item["object_id"],str(item.get("label") or item),x,y,2.4,.8,14,True)
        elif typ=="table":
            rows=c["rows"]; shape=slide.shapes.add_table(len(rows)+1,len(c["headers"]),Inches(.75),Inches(1.9),Inches(11.8),Inches(3.8)); tag(shape,"table",s["accessibility"]["alt_text"])
            table=shape.table
            for j,v in enumerate(c["headers"]): table.cell(0,j).text=str(v["label"])
            for i,row in enumerate(rows):
                values=row.get("cells",row) if isinstance(row,dict) else row
                for j,v in enumerate(values): table.cell(i+1,j).text=str(v.get("value",v) if isinstance(v,dict) else v)
        elif typ in ("recommendation","cta"):
            main=c.get("recommendation") or c.get("cta"); detail=c.get("rationale") or s["implication"]
            rect(slide,"visual",margin,1.95,1.0,2.05,pal["accent"],s["accessibility"]["alt_text"])
            textbox(slide,"content-1",main,margin+1.25,2.1,10.2,1.65,28,True,fg,PP_ALIGN.CENTER,alt=main)
            textbox(slide,"content-2",detail,1.25,4.35,10.8,.8,17,False,fg,PP_ALIGN.CENTER,alt=detail)
        textbox(slide,"implication",s["implication"],margin,5.72,13.333-2*margin,.52,15,True,fg,alt=s["implication"])
        textbox(slide,"source-footer","Sources: "+"; ".join(s["source_footer"]),margin,6.65,13.333-2*margin,.3,token["type_pt"]["source"],False,fg,alt="Source identifiers: "+", ".join(s["source_footer"]))
        notes=slide.notes_slide.notes_text_frame
        notes.text=json.dumps({"slide_id":s["slide_id"],"notes":s["notes"],"claim_ids":s["claim_ids"],"evidence_ids":s["evidence_ids"],"source_footer":s["source_footer"],"reading_order":s["reading_order"],"cta":s["content"].get("cta") if s["type"]=="cta" else None},sort_keys=True)
        reorder(slide,s["reading_order"])
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); prs.save(out)
    print(json.dumps({"status":"rendered","slides":len(prs.slides),"output":str(out)})); return 0
if __name__=="__main__": raise SystemExit(main())
