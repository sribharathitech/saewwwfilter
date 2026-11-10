"""Refresh sitemap from canonical pages and published documents, using Git dates."""
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://" + (ROOT / "CNAME").read_text().strip()
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
IST = timezone(timedelta(hours=5, minutes=30))
class Metadata(HTMLParser):
    def __init__(self):
        super().__init__(); self.canonical = None; self.noindex = False; self.redirect = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "link" and a.get("rel") == "canonical": self.canonical = a.get("href")
        if tag == "meta":
            if a.get("name", "").lower() == "robots": self.noindex = "noindex" in a.get("content", "").lower()
            if a.get("http-equiv", "").lower() == "refresh": self.redirect = True

def last_modified(path):
    name = path.relative_to(ROOT).as_posix()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--", name], cwd=ROOT, text=True).strip()
    if dirty: return datetime.now(IST).date().isoformat()
    value = subprocess.check_output(["git", "log", "-1", "--format=%cI", "--", name], cwd=ROOT, text=True).strip()
    return datetime.fromisoformat(value).astimezone(IST).date().isoformat() if value else None

def refresh():
    entries = {}
    for path in ROOT.rglob("*.html"):
        if any(p in {".git", ".qa", "partials"} for p in path.relative_to(ROOT).parts): continue
        metadata = Metadata(); metadata.feed(path.read_text(encoding="utf-8"))
        if metadata.noindex or metadata.redirect or not metadata.canonical: continue
        url = metadata.canonical
        assert url.startswith(BASE + "/") and "#" not in url and "?" not in url, url
        assert url not in entries, "Duplicate canonical: " + url
        entries[url] = last_modified(path)
    pages = len(entries)
    for path in sorted((ROOT / "assets/documents").glob("*.pdf")):
        assert path.read_bytes().startswith(b"%PDF"), path
        entries[BASE + "/" + path.relative_to(ROOT).as_posix()] = last_modified(path)
    ET.register_namespace("", NS)
    sitemap = ET.Element("{" + NS + "}urlset")
    for url, date in sorted(entries.items()):
        node = ET.SubElement(sitemap, "{" + NS + "}url")
        ET.SubElement(node, "{" + NS + "}loc").text = url
        if date: ET.SubElement(node, "{" + NS + "}lastmod").text = date
    ET.indent(sitemap, space="  ")
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(sitemap, encoding="unicode") + "\n", encoding="utf-8", newline="\n")
    print(f"Sitemap refreshed: {pages} canonical pages and {len(entries)-pages} PDFs")
if __name__ == "__main__": refresh()
