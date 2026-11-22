#!/usr/bin/env python3
"""Build downloadable CV files (Markdown, Word, PDF) from the site's CV data.

Reads _data/cv.yml (and the talks list in _data/media.yml) and writes:
  assets/cv/Ramzy_Muliawan_CV.md
  assets/cv/Ramzy_Muliawan_CV.docx   (via pandoc, from the Markdown)
  assets/cv/Ramzy_Muliawan_CV.pdf    (via WeasyPrint, from HTML)

Runs in the Deploy workflow before the Jekyll build, so the files always match
the CV page. Requirements: pyyaml, pypandoc_binary, weasyprint.

Usage: python3 bin/build_cv_downloads.py [repo_root]
"""

import html
import re
import sys
from pathlib import Path

import yaml

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
BASENAME = "Ramzy_Muliawan_CV"
SITE_URL = "https://ramzymuliawan.github.io"
CATEGORIES = ["wikimedia", "digital-rights", "other"]
CATEGORY_TITLES = {"wikimedia": "Wikimedia", "digital-rights": "Digital rights", "other": "Other"}


def fmt_date(value):
    if value is None:
        return ""
    s = str(value)
    parts = s.split("-")
    if len(parts) > 1:
        return f"{MONTHS[int(parts[1]) - 1]} {parts[0]}"
    return s


def span(entry):
    start = fmt_date(entry.get("start_date"))
    if "end_date" not in entry or entry.get("end_date") is None:
        return f"{start} – present" if start else ""
    end = fmt_date(entry.get("end_date"))
    return start if start == end else f"{start} – {end}"


def md_links_to_html(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # pandoc language spans: [text]{lang=id}
    return re.sub(r"\[(.+?)\]\{lang=([a-z-]+)\}", r'<span lang="\2">\1</span>', text)


def build_markdown(cv, talks):
    s = cv["sections"]
    out = [f"# {cv['name']}", "", f"{cv['label']} · {cv['location']} · {cv['email']}", ""]

    def roles(title, items):
        out.extend([f"## {title}", ""])
        for e in items:
            meta = " · ".join(x for x in [e.get("company"), e.get("location"), span(e)] if x)
            out.extend([f"### {e['position']}", "", meta, ""])
            for h in e.get("highlights") or []:
                out.append(f"- {h}")
            if e.get("highlights"):
                out.append("")

    roles("Experience", s["Experience"])

    out.extend(["## Volunteer and service", ""])
    for cat in CATEGORIES:
        vols = [v for v in s["Volunteer"] if v.get("category") == cat]
        if not vols:
            continue
        out.extend([f"### {CATEGORY_TITLES[cat]}", ""])
        seen = []
        for v in vols:
            if v["company"] not in seen:
                seen.append(v["company"])
        for org in seen:
            out.extend([f"#### {org}", ""])
            for v in [x for x in vols if x["company"] == org]:
                meta = " · ".join(x for x in [v.get("location"), span(v)] if x)
                out.append(f"- **{v['position']}** · {meta}")
                for h in v.get("highlights") or []:
                    out.append(f"    - {h}")
            out.append("")

    out.extend(["## Education", ""])
    for e in s["Education"]:
        heading = e["studyType"] + (f", {e['area']}" if e.get("area") else "")
        meta = " · ".join(x for x in [e.get("institution"), e.get("location"), span(e)] if x)
        out.extend([f"### {heading}", "", meta, ""])
        for h in e.get("highlights") or []:
            out.append(f"- {h}")
        out.append("")

    out.extend(["## Publications", ""])
    for p in s["Publications"]:
        year = str(p.get("releaseDate", "")).split("-")[0]
        url = p.get("url")
        if url and url.startswith("/"):
            url = SITE_URL + url
        title = f"[{p['title']}]({url})" if url else f"*{p['title']}*"
        if p.get("lang"):
            title = f"[{title}]{{lang={p['lang']}}}"  # pandoc span: marks the language in Word and PDF
        if p.get("archive"):
            title += f" ([Internet Archive version]({p['archive']}))"
        out.append(f"- {', '.join(p['authors'])} ({year}). {title}. {p['publisher']}.")
    out.append("")

    out.extend(["## Talks", ""])
    for cat in CATEGORIES:
        ts = [t for t in talks if t.get("category") == cat]
        if not ts:
            continue
        out.extend([f"### {CATEGORY_TITLES[cat]}", ""])
        for t in ts:
            when = f" ({t['date']})" if t.get("date") else ""
            link = f"[{t['title']}]({t['url']})"
            if t.get("lang"):
                link = f"[{link}]{{lang={t['lang']}}}"
            if t.get("archive"):
                link += f" ([Internet Archive version]({t['archive']}))"
            out.append(f"- {t['outlet']}: {link}{when}")
        out.append("")

    out.extend(["## Licenses, fellowships, and certifications", ""])
    for c in s["Certificates"]:
        when = f" ({c['date']})" if c.get("date") else ""
        name = f"[{c['name']}]({c['url']})" if c.get("url") else c["name"]
        if c.get("lang"):
            name = f"[{name}]{{lang={c['lang']}}}"
        if c.get("archive"):
            name += f" ([Internet Archive version]({c['archive']}))"
        out.append(f"- {name}, {c['issuer']}{when}")
    out.append("")

    out.extend(["## Awards", ""])
    for a in s["Awards"]:
        arch = f" ([Internet Archive version]({a['archive']}))" if a.get("archive") else ""
        out.append(f"- {a['title']}, {a['awarder']} ({a['date']}){arch}")
    out.append("")

    out.extend(["## Affiliations", ""])
    for a in s["Affiliations"]:
        out.append(f"- {a['bullet']}")
    out.append("")
    return "\n".join(out)


def build_html(markdown_text, font_dir):
    """Small Markdown-to-HTML pass for the fixed structure produced above."""
    lines = markdown_text.split("\n")
    body, in_list = [], False
    for line in lines:
        if line.startswith("- ") or line.startswith("    - "):
            if not in_list:
                body.append("<ul>")
                in_list = True
            nested = line.startswith("    - ")
            item = line.strip()[2:]
            item = md_links_to_html(item)
            item = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", item)
            item = re.sub(r"\*([^*]+)\*", r"<cite>\1</cite>", item)
            body.append(f'<li class="sub">{item}</li>' if nested else f"<li>{item}</li>")
            continue
        if in_list:
            body.append("</ul>")
            in_list = False
        if line.startswith("#### "):
            body.append(f"<h4>{html.escape(line[5:])}</h4>")
        elif line.startswith("### "):
            body.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            body.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            body.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.strip():
            body.append(f'<p class="meta">{md_links_to_html(line)}</p>')
    if in_list:
        body.append("</ul>")

    regular = (font_dir / "PlusJakartaSans-Variable.woff2").resolve().as_uri()
    italic = (font_dir / "PlusJakartaSans-Italic-Variable.woff2").resolve().as_uri()
    css = f"""
    @font-face {{ font-family: "Plus Jakarta Sans"; src: url("{regular}"); font-weight: 200 800; font-style: normal; }}
    @font-face {{ font-family: "Plus Jakarta Sans"; src: url("{italic}"); font-weight: 200 800; font-style: italic; }}
    @page {{ size: A4; margin: 18mm 17mm; @bottom-right {{ content: counter(page) " / " counter(pages); font-size: 8.5pt; color: #64748b; }} }}
    body {{ font-family: "Plus Jakarta Sans", sans-serif; font-size: 10pt; line-height: 1.5; color: #1e293b; }}
    h1 {{ font-size: 20pt; margin: 0 0 2pt; }}
    h1 + p.meta {{ margin-bottom: 10pt; }}
    h2 {{ font-size: 12.5pt; color: #0f766e; border-bottom: 0.6pt solid #e2e8f0; padding-bottom: 2pt; margin: 14pt 0 6pt; }}
    h3 {{ font-size: 10.5pt; margin: 8pt 0 0; }}
    h4 {{ font-size: 10pt; margin: 6pt 0 1pt; }}
    li.sub {{ margin-left: 14pt; list-style-type: circle; }}
    p.meta {{ color: #64748b; margin: 0 0 3pt; }}
    ul {{ margin: 0 0 4pt; padding-left: 14pt; }}
    li::marker {{ font-family: "Plus Jakarta Sans", sans-serif; }}
    li {{ margin-bottom: 2pt; }}
    a {{ color: #0f766e; text-decoration: underline; }}
    h2, h3, h4 {{ break-after: avoid; }}
    """
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        "<title>Ramzy Muliawan – CV</title>"
        f"<style>{css}</style></head><body>" + "\n".join(body) + "</body></html>"
    )


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    cv = yaml.safe_load((root / "_data/cv.yml").read_text(encoding="utf-8"))["cv"]
    talks = yaml.safe_load((root / "_data/media.yml").read_text(encoding="utf-8")).get("talks", [])
    out_dir = root / "assets/cv"
    out_dir.mkdir(parents=True, exist_ok=True)

    md_text = build_markdown(cv, talks)
    md_path = out_dir / f"{BASENAME}.md"
    md_path.write_text(md_text, encoding="utf-8")

    import pypandoc

    # The name becomes the Word document's Title (also its document property), so drop the "# " line.
    docx_md = md_text.split("\n", 1)[1]
    pypandoc.convert_text(docx_md, "docx", format="markdown", outputfile=str(out_dir / f"{BASENAME}.docx"),
                          extra_args=["--metadata", f"title={cv['name']}", "--metadata", "lang=en"])

    from weasyprint import HTML

    page = build_html(md_text, root / "assets/fonts/plus-jakarta-sans")
    HTML(string=page, base_url=str(root)).write_pdf(str(out_dir / f"{BASENAME}.pdf"),
                                                     pdf_variant="pdf/ua-1")
    for ext in ("md", "docx", "pdf"):
        p = out_dir / f"{BASENAME}.{ext}"
        print(f"wrote {p.relative_to(root)} ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
