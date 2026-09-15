from pathlib import Path
import subprocess
import tempfile

from lxml import etree


ROOT = Path(__file__).parent
REVISION = "1d08be9288303d7f35ddf51c4af476589597a96d"
REPOSITORY = "https://github.com/Cannamatrix-team/CannamatrixAI"
CODE = f"{REPOSITORY}/blob/{REVISION}"
SVG = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"


def link_source_rows(svg):
    root = etree.fromstring(svg.encode())
    for element in list(root.iter()):
        if element.tag not in (f"{{{SVG}}}text", f"{{{SVG}}}tspan"):
            continue
        path = (element.text or "").strip()
        if not path.startswith(("frontend/", "components/", ".github/", "supabase/")):
            continue
        if len(element):
            continue
        kind = "tree" if path.endswith("/") else "blob"
        href = f"{REPOSITORY}/{kind}/{REVISION}/{path}"
        anchor = etree.Element(f"{{{SVG}}}a", {
            "href": href,
            f"{{{XLINK}}}href": href,
            "target": "_blank",
            "rel": "noopener noreferrer",
            "class": "source-link",
            "aria-label": f"Open source: {path}",
        })
        element.getparent().replace(element, anchor)
        anchor.append(element)
    return etree.tostring(root, encoding="unicode")


page = (ROOT / "page.template.html").read_text()
with tempfile.TemporaryDirectory() as temp:
    for name in ("locations", "sequence", "data", "overview"):
        source = ROOT / "diagrams" / f"{name}.d2"
        if source.exists():
            output = Path(temp) / f"{name}.svg"
            layout = "elk" if name == "locations" else "dagre"
            subprocess.run([
                "d2", "--layout", layout, "--pad", "35", "--no-xml-tag",
                str(source), str(output),
            ], check=True)
        else:
            output = ROOT / "diagrams" / f"{name}.svg"
        page = page.replace(f"@FIGURE_{name.upper()}@", link_source_rows(output.read_text()))
page = page.replace("@CODE@", CODE).replace("@TREE@", f"{REPOSITORY}/tree/{REVISION}")
page = page.replace("@REV_SHORT@", REVISION[:8])
(ROOT / "index.html").write_text(page)
