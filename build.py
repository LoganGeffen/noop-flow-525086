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
SCREEN_LINKS = {
    "Open platform": "https://cannamatrix-ai.vercel.app/dev/noop",
    "Open login": "https://cannamatrix-ai.vercel.app/login",
    "Open Vercel": "https://vercel.com/cannamatrix1/cannamatrix-ai/deployments",
    "Open light workflow": f"{REPOSITORY}/actions/workflows/noop.yml",
    "Open heavy workflow": f"{REPOSITORY}/actions/workflows/noop-baked.yml",
    "Open EC2 instances": "https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#Instances:",
    "Open launch template": "https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#LaunchTemplates:",
    "Open SSM commands": "https://us-east-1.console.aws.amazon.com/systems-manager/run-command?region=us-east-1",
    "Open S3 outputs": "https://s3.console.aws.amazon.com/s3/buckets/cmx-tenant-internal-050752621192?region=us-east-1&prefix=genotype-results%2F&showversions=false",
    "Open Supabase": "https://supabase.com/dashboard/project/mydyodpsytaznskiemna/sql/new",
    "Open Supabase Auth": "https://supabase.com/dashboard/project/mydyodpsytaznskiemna/auth/users",
}


def link_rows(svg):
    root = etree.fromstring(svg.encode())
    for element in list(root.iter()):
        if element.tag not in (f"{{{SVG}}}text", f"{{{SVG}}}tspan"):
            continue
        if len(element):
            continue
        label = (element.text or "").strip()
        if label in SCREEN_LINKS:
            href = SCREEN_LINKS[label]
            css_class = "screen-link"
        elif label.startswith(("frontend/", "components/", ".github/", "supabase/")):
            kind = "tree" if label.endswith("/") else "blob"
            href = f"{REPOSITORY}/{kind}/{REVISION}/{label}"
            css_class = "source-link"
        else:
            continue
        anchor = etree.Element(f"{{{SVG}}}a", {
            "href": href,
            f"{{{XLINK}}}href": href,
            "target": "_blank",
            "rel": "noopener noreferrer",
            "class": css_class,
            "aria-label": label if css_class == "screen-link" else f"Open source: {label}",
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
        page = page.replace(f"@FIGURE_{name.upper()}@", link_rows(output.read_text()))
page = page.replace("@CODE@", CODE).replace("@TREE@", f"{REPOSITORY}/tree/{REVISION}")
page = page.replace("@REV_SHORT@", REVISION[:8])
(ROOT / "index.html").write_text(page)
