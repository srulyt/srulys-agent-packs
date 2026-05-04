# Inputs — smoke-template-mode

Place a real corporate template at `templates/corporate-2026.pptx` before
running. For a quick fixture, any minimal `.pptx` produced by python-pptx
will do; the test verifies *path round-trip*, not theme correctness.

Quick generator:

```python
from pptx import Presentation
prs = Presentation()
prs.slides.add_slide(prs.slide_layouts[6])
prs.save("templates/corporate-2026.pptx")
```
