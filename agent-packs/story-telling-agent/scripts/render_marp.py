import argparse, html, json
from pathlib import Path
def esc(v): return html.escape(str(v))
def chart_semantics(c):
 colors={"categorical":["accent","positive","warning","text"],"sequential":["accent","text","positive","warning"],"diverging":["warning","accent","positive","text"],"status":["positive","warning","text","accent"]}[c["color_semantics"]]
 explicit=c.get("explicit_axis") or {}
 attrs=f'data-chart-type="{esc(c["chart_type"])}" data-axis-policy="{esc(c["axis_policy"])}" data-color-semantics="{esc(c["color_semantics"])}" data-render-mode="{esc(c["render_mode"])}"'
 axis=f'<figcaption>X: {esc(explicit.get("x_title","categories"))} [{esc(explicit.get("x_min","auto"))}, {esc(explicit.get("x_max","auto"))}] · Y: {esc(explicit.get("y_title",c["units"]))} [{esc(explicit.get("y_min","auto"))}, {esc(explicit.get("y_max","auto"))}]</figcaption>'
 if c["render_mode"]=="deterministic-image" or c["chart_type"]=="scatter":
  points=[]; xs=[]
  for i,label in enumerate(c["categories"]):
   try: xs.append(float(label))
   except ValueError: xs.append(float(i))
  all_y=[float(v) for s in c["series"] for v in s["values"] if v is not None] or [0,1]
  xmin,xmax=explicit.get("x_min",min(xs)),explicit.get("x_max",max(xs) or 1); ymin,ymax=explicit.get("y_min",min(0,min(all_y))),explicit.get("y_max",max(all_y))
  if xmax==xmin: xmax=xmin+1
  if ymax==ymin: ymax=ymin+1
  for si,series in enumerate(c["series"]):
   coords=[]
   for x,y in zip(xs,series["values"]):
    if y is None: continue
    px=50+(x-xmin)/(xmax-xmin)*700; py=330-(float(y)-ymin)/(ymax-ymin)*280
    coords.append((px,py))
   if c["chart_type"]=="scatter":
    points += [f'<circle cx="{x:.2f}" cy="{y:.2f}" r="7" class="series-{colors[si%len(colors)]}"><title>{esc(series["name"])}</title></circle>' for x,y in coords]
   else:
    points.append(f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in coords)}" class="series-{colors[si%len(colors)]}"/>')
  svg=f'<svg viewBox="0 0 800 360" role="img" aria-label="{esc(c["focal_datum"])}"><path d="M50 30V330H770"/>'+"".join(points)+"</svg>"
  return f'<figure class="chart deterministic" {attrs}>{svg}{axis}</figure>'
 rows=["| Category | "+" | ".join(esc(x["name"]) for x in c["series"])+" |","|---|"+"|".join("---:" for _ in c["series"])+"|"]
 def value(v): return "—" if v is None and c["missing_value_policy"] in ("gap","annotate","exclude") else ("0" if v is None else esc(v))
 rows += ["| "+esc(cat)+" | "+" | ".join(value(x["values"][i]) for x in c["series"])+" |" for i,cat in enumerate(c["categories"])]
 return f'<figure class="chart editable" {attrs}>{axis}</figure>\n'+"\n".join(rows)
def body(s):
 c=s["content"]; t=s["type"]
 if t in ("title","section"): return f'<div class="hero">{esc(c.get("subtitle") or c.get("section_label"))}</div>'
 if t=="assertion-evidence": return '<div class="cards">'+"".join(f'<div id="{esc(x["object_id"])}">{esc(x["text"])}</div>' for x in c["evidence_blocks"])+"</div>"
 if t=="big-number": return f'<div class="big">{esc(c["value"])} <small>{esc(c["unit"])}</small></div><p>{esc(c["context"])}</p>'
 if t=="comparison": return f'<div class="columns"><div>{esc(c["left"])}</div><div>{esc(c["right"])}</div></div><p>{esc(c["comparison_basis"])}</p>'
 if t in ("process","timeline"): return '<ol>'+"".join(f'<li id="{esc(x["object_id"])}">{esc(x.get("label") or x.get("title") or x)}</li>' for x in c["steps" if t=="process" else "events"])+"</ol>"
 if t=="chart":
  policy=f'<p class="chart-policy">Relationship: {esc(c["relationship"])} · Type: {esc(c["chart_type"])} · Axis: {esc(c["axis_policy"])} · Missing: {esc(c["missing_value_policy"])} · Color: {esc(c["color_semantics"])} · Mode: {esc(c["render_mode"])}</p>'
  return policy+"\n"+chart_semantics(c)+f'\n\n**{esc(c["focal_datum"])} — {esc(c["annotation"])}** ({esc(c["units"])})'
 if t=="image-led": return f'<figure><img style="object-position:{esc(c["crop_focal_point"])}" src="{esc(c["source"])}" alt="{esc(c["alt_text"])}"><figcaption>{esc(c["license"])}</figcaption></figure>'
 if t=="quote": return f'<blockquote>{esc(c["quote"])}</blockquote><p>— {esc(c["attribution"])}</p>'
 if t=="matrix":
  items="".join(f'<span id="{esc(x["object_id"])}" class="matrix-item" data-x="{x["x"]}" data-y="{x["y"]}" style="left:{x["x"]*100:.2f}%;bottom:{x["y"]*100:.2f}%">{esc(x["label"])}</span>' for x in c["items"])
  return f'<figure class="matrix" data-x-axis="{esc(c["x_axis"])}" data-y-axis="{esc(c["y_axis"])}"><span class="axis-x">{esc(c["x_axis"])}</span><span class="axis-y">{esc(c["y_axis"])}</span>{items}</figure>'
 if t=="table": return "| "+" | ".join(esc(x["label"]) for x in c["headers"])+" |\n|"+"|".join("---" for _ in c["headers"])+"|\n"+"\n".join("| "+" | ".join(esc(x["value"]) for x in r)+" |" for r in c["rows"])
 if t=="recommendation": return f'## {esc(c["recommendation"])}\n\n{esc(c["rationale"])}\n\nOwner: {esc(c["owner"])} · Next: {esc(c["next_step"])}'
 if t=="cta": return f'## {esc(c["cta"])}\n\nOwner: {esc(c["owner"])} · Timing: {esc(c["timing"])}'
 return esc(s["core_assertion"])
def main():
 p=argparse.ArgumentParser(); p.add_argument("--spec",required=True); p.add_argument("--output",required=True); p.add_argument("--registry"); a=p.parse_args()
 d=json.loads(Path(a.spec).read_text(encoding="utf-8")); registry=Path(a.registry) if a.registry else Path(__file__).resolve().parents[1]/"design-systems"/"registry.json"; systems=json.loads(registry.read_text())["systems"]; tok=next(x for x in systems if x["id"]==d["design_system_id"]); pal=tok["palette"]
 grid=tok["grid"]; gap=tok["spacing_pt"][3]
 css=f"""<style>:root{{--bg:{pal['background']};--fg:{pal['text']};--accent:{pal['accent']};--positive:{pal['positive']};--warning:{pal['warning']}}}section{{background:var(--bg);color:var(--fg);font-family:{tok['fonts']['body'][0]},Arial;padding:{grid['margin_in']}in;display:grid;grid-template-columns:repeat({grid['columns']},1fr);gap:{grid['gutter_in']}in}}section>*{{grid-column:1/-1}}section.bg-accent,section.bg-positive,section.bg-warning{{color:white}}section.bg-accent{{background:var(--accent)}}section.bg-positive{{background:var(--positive)}}section.bg-warning{{background:var(--warning)}}h1{{color:var(--accent);font-family:{tok['fonts']['heading'][0]},Arial;font-size:{tok['type_pt']['title']}pt}}.bg-accent h1,.bg-positive h1,.bg-warning h1{{color:white}}.hero,.big{{font-size:44pt;text-align:center;margin-top:{tok['spacing_pt'][-1]}pt}}.columns,.cards{{display:grid;grid-template-columns:1fr 1fr;gap:{gap}pt}}figure img{{width:100%;height:4in;object-fit:cover}}small,.sources{{font-size:{tok['type_pt']['source']}pt}}.chart-policy{{font-size:{tok['type_pt']['source']}pt}}.chart svg{{width:100%;height:3.2in}}.chart path{{fill:none;stroke:var(--fg);stroke-width:2}}.chart polyline{{fill:none;stroke-width:5}}.series-accent{{stroke:var(--accent);fill:var(--accent)}}.series-positive{{stroke:var(--positive);fill:var(--positive)}}.series-warning{{stroke:var(--warning);fill:var(--warning)}}.series-text{{stroke:var(--fg);fill:var(--fg)}}.matrix{{position:relative;height:3.4in;border-left:2px solid var(--fg);border-bottom:2px solid var(--fg)}}.matrix-item{{position:absolute;transform:translate(-50%,50%);background:var(--accent);color:white;padding:5px 9px;border-radius:8px}}.axis-x{{position:absolute;bottom:-28px;left:45%}}.axis-y{{position:absolute;left:-55px;top:45%;transform:rotate(-90deg)}}</style>"""
 parts=["---","marp: true","paginate: true","html: true","---",css]
 for s in d["slides"]:
  semantic={"index":s["index"],"slide_id":s["slide_id"],"title":s["title"],"claim_ids":s["claim_ids"],"evidence_ids":s["evidence_ids"],"source_footer":s["source_footer"],"notes":s["notes"],"cta":s["content"].get("cta") if s["type"]=="cta" else None}
  parts += ["---",f"<!-- _class: layout-{esc(s['layout_family'])} recipe-{esc(s['recipe'])} bg-{esc(s['background_role'])} -->",f"<!-- story-semantic: {json.dumps(semantic,sort_keys=True)} -->",f"# {esc(s['title'])}",f"**{esc(s['core_assertion'])}**",body(s),f'<p class="implication">{esc(s["implication"])}</p>',f'<p class="sources">Sources: {esc("; ".join(s["source_footer"]))}</p>',f"<!-- _notes: {json.dumps(s['notes'],sort_keys=True)} -->"]
 Path(a.output).write_text("\n".join(parts)+"\n",encoding="utf-8",newline="\n"); print(json.dumps({"status":"rendered","slides":len(d["slides"]),"output":a.output})); return 0
if __name__=="__main__": raise SystemExit(main())
