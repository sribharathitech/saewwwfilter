"""Apply shared action markup to generated pages; safe to run repeatedly."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
ICONS = {
    "arrow": '<path d="M4 12h16m-6-6 6 6-6 6"/>',
    "external": '<path d="M14 3h7v7M21 3l-9 9M10 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
}
VOID = {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
class Actions(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source=source;self.lines=[0];self.stack=[];self.active=None;self.edits=[]
        self.lines.extend(m.end() for m in re.finditer("\n",source))
    def source_position(self):
        row,col=self.getpos();return self.lines[row-1]+col
    def handle_starttag(self, tag, attrs):
        data=dict(attrs);classes=data.get("class","").split()
        if tag=="a" and any(t=="main" for t,a in self.stack):
            ancestors={c for t,a in self.stack for c in a.get("class","").split()}
            library=any(a.get("id")=="catalogues-presentations" for t,a in self.stack)
            selected=(set(classes)&{"button","text-link"} or ancestors&{"card","related-links","pdf-fallback","hero-actions","pulp-technical-footer","carbon-grade-footer","lenticular-technical-footer"})
            if selected and not library and "site-action" not in classes:
                href=data.get("href","")
                primary="button" in classes or ("contact" in href and "related-links" not in ancestors)
                icon="external" if ".pdf" in href.lower() else "mail" if "contact" in href else "arrow"
                self.active=(self.source_position(),self.get_starttag_text(),data,primary,icon)
        if tag not in VOID:self.stack.append((tag,data))
    def handle_endtag(self,tag):
        if tag=="a" and self.active:
            start,opening,data,primary,icon=self.active;end=self.source_position()
            content=self.source[start+len(opening):end]
            content=re.sub(r'<span\s+aria-hidden="true">(?:&rarr;|\u2192)</span>',"",content)
            content=re.sub(r'\s*(?:\u2192|&rarr;)\s*$',"",content).strip()
            classes=data.get("class","")+" site-action "+("action-primary" if primary else "action-secondary")
            if "class" in data:opening=re.sub(r'class=([\"\x27]).*?\1','class="'+classes.strip()+'"',opening)
            else:opening=opening[:-1]+' class="'+classes.strip()+'">'
            svg='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+ICONS[icon]+'</svg>'
            self.edits.append((start,end+4,opening+'<span>'+content+'</span>'+svg+'</a>'));self.active=None
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:self.stack=self.stack[:i];break

def style_pages():
    count=0
    for path in ROOT.rglob("*.html"):
        if any(p in {".qa",".git","partials"} for p in path.relative_to(ROOT).parts):continue
        source=path.read_text(encoding="utf-8")
        if 'http-equiv="refresh"' in source:continue
        parser=Actions(source);parser.feed(source)
        for start,end,value in reversed(parser.edits):source=source[:start]+value+source[end:]
        source=re.sub(r'(href="[^\"]*assets/styles\.css)(?:\?[^\"]*)?"',r'\1?v=20261110-depth-guide"',source)
        if source!=path.read_text(encoding="utf-8"):path.write_text(source,encoding="utf-8",newline="\n")
        count+=len(parser.edits)
    print(f"Styled {count} website actions")
if __name__=="__main__":style_pages()
