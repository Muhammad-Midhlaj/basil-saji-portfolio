"""Generates one viewer page per document at reports/<slug>/index.html.

Run:  python build_reports.py
Each page shows the document page-by-page (works on phones) plus a PDF download,
so the link can be pasted next to the matching entry in Basil's CV.
"""
import glob
import html
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

DOCS = [
    {
        "slug": "final-year-project",
        "file": "final-year-project-simo-converter",
        "kind": "Final-year project report",
        "title": "PV-based Single-Input Multiple-Output Two-Phase Interleaved DC-DC Converter",
        "meta": ["B.E. EEE (Marine)", "AMET University", "2023", "34 slides"],
        "summary": "A SEPIC-Ćuk two-phase interleaved converter that takes a 150 V solar PV input and supplies a "
                   "battery-charging port, a DC motor, and an inverter-fed AC load. The phases are switched 180° apart "
                   "so their ripple currents cancel. It was simulated in MATLAB/Simulink and built in hardware around "
                   "a PIC16F877A, IRF840 MOSFETs and an IR2110 driver.",
        "facts": [("Guide", "Dr. T. Baldwin Immanuel, Assoc. Prof., EEE"), ("Input", "150 V DC from PV panel"),
                  ("Outputs", "2 × DC + 1 × AC (inverter)"), ("Control", "PWM + PI controller")],
        "points": ["Literature review of interleaved and multiport converters", "Existing vs. proposed block diagram",
                   "SEPIC-Ćuk operation and PWM phase shifting", "Simulink model with motor, inverter and battery results",
                   "Hardware: MCU, MOSFET, gate driver and power supply", "Oscilloscope captures of PWM and inverter output"],
    },
    {
        "slug": "internship-report",
        "file": "internship-report-power-electronics",
        "kind": "Internship report",
        "title": "Recent Trends in Power Electronics Applications",
        "meta": ["Pantech e Learning, Chennai", "27 Dec 2021 – 11 Jan 2022", "16 pages"],
        "summary": "A daily internship log written during Basil's third year of the B.E. degree. It covers power "
                   "conversion classes, inverter applications, motor drives, smart grid integration, simulation tools, "
                   "and industry trends in EVs, 5G and energy storage.",
        "facts": [("Organisation", "Pantech e Learning"), ("Duration", "2 weeks"), ("Reg. No.", "AEE19013"),
                  ("Certificate", "PA-INTERN-21-22-2572")],
        "points": ["AC-DC / DC-AC / DC-DC / AC-AC converters", "Active power filters, UPS and VAR compensation",
                   "Scalar vs. vector-controlled AC drives", "Smart grid, PV inverters and HVDC",
                   "PLECS, PSIM and MATLAB/Simulink simulation", "Trends: EVs, GaN for 5G, renewables and ESS"],
        "related": ("internship-certificate", "View the completion certificate"),
    },
    {
        "slug": "internship-certificate",
        "file": "internship-certificate-pantech",
        "kind": "Certificate of completion",
        "title": "Internship: Recent Trends in Power Electronics Application",
        "meta": ["Pantech e Learning, Chennai", "27 Dec 2021 – 11 Jan 2022"],
        "summary": "Certificate confirming that Basil Saji of AMET University completed the internship on Recent "
                   "Trends in Power Electronics Application at Pantech e Learning, Chennai.",
        "facts": [("Certificate No.", "PA-INTERN-21-22-2572"), ("Issued by", "Srinivasan N., Director, Pantech")],
        "points": [],
        "related": ("internship-report", "Read the full internship report"),
    },
    {
        "slug": "eto-training",
        "file": "eto-training-record",
        "kind": "Training record",
        "title": "Electro-Technical Officer (ETO): Shop-Floor Training Record",
        "meta": ["AMET University", "From 19 Jan 2024", "17 weeks", "Grade A"],
        "summary": "The official statement of ETO training under STCW Section A-III/6, approved by the Directorate "
                   "General of Shipping, Govt. of India. It lists 19 competencies with 438 theory hours and 197 "
                   "practical hours. Overall grade A, with ability and conduct both rated Very Good.",
        "facts": [("Certificate No.", "40100136012400127"), ("MTI No.", "401001"), ("DGS approval", "No. 100047"),
                  ("Hours", "438 theory + 197 practical")],
        "points": ["Electrical, electronic and control systems", "Propulsion and auxiliary machinery automation",
                   "Generators and distribution systems", "Bridge navigation and communication equipment",
                   "Deck machinery and cargo handling", "Fire fighting and pollution prevention"],
    },
    {
        "slug": "degree-certificate",
        "file": "degree-certificate-be-eee-marine",
        "kind": "Degree certificate",
        "title": "Bachelor of Engineering: Electrical & Electronics Engineering (Marine)",
        "meta": ["AMET University, Chennai", "First Class", "Sept 2023"],
        "summary": "Degree certificate from AMET (Deemed to be University), Chennai, conferring the B.E. in Electrical "
                   "and Electronics Engineering (Marine) with First Class, from the examination held in September 2023.",
        "facts": [("Register No.", "AEE19013"), ("Class", "First Class"), ("Issued", "17 Nov 2023")],
        "points": [],
    },
]

HEAD = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | Basil Saji</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title} | Basil Saji"><meta property="og:description" content="{desc}">
<meta property="og:image" content="../../assets/pages/{file}-01.jpg"><meta name="theme-color" content="#070b10">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23070b10'/%3E%3Cpath d='M18 4 8 18h7l-2 10 11-15h-7z' fill='%23f0913a'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/site.css">
</head><body>
<nav class="nav"><div class="wrap">
  <a class="logo" href="../../"><svg viewBox="0 0 32 32" aria-hidden="true"><rect x="1" y="1" width="30" height="30" rx="8" fill="none" stroke="#1c2a38" stroke-width="2"/><path d="M18 5 8 18h7l-2 9 11-14h-7z" fill="#f0913a"/></svg>BASIL_SAJI</a>
  <ul><li><a href="../../#project">Project</a></li><li><a href="../../#internship">Internship</a></li><li><a href="../../#eto">ETO</a></li><li><a href="../../#documents">All documents</a></li></ul>
</div></nav>
"""


def page(d):
    e = html.escape
    pages = sorted(glob.glob(os.path.join(ROOT, "assets", "pages", d["file"] + "-*.jpg")))
    n = len(pages)
    unit = "slide" if "project" in d["slug"] else "page"
    figs = "\n".join(
        f'<figure><img src="../../assets/pages/{os.path.basename(p)}" alt="{e(d["title"])}, {unit} {i}" '
        f'loading="{"eager" if i < 3 else "lazy"}"><figcaption>{unit.upper()} {i} / {n}</figcaption></figure>'
        for i, p in enumerate(pages, 1))
    chips = "".join(f'<span class="chip{" c" if i == 0 else ""}">{e(m)}</span>' for i, m in enumerate(d["meta"]))
    facts = "".join(f"<tr><td>{e(k)}</td><td>{e(v)}</td></tr>" for k, v in d["facts"])
    pts = "".join(f"<li>{e(p)}</li>" for p in d["points"])
    pts_card = f'<div class="card"><div class="label">Inside this document</div><ul>{pts}</ul></div>' if pts else ""
    rel = ""
    if d.get("related"):
        rel = f'<a class="btn" href="../{d["related"][0]}/">{e(d["related"][1])} →</a>'
    pdf = f'../../assets/docs/{d["file"]}.pdf'
    return HEAD.format(title=e(d["title"]), desc=e(d["summary"][:155]), file=d["file"]) + f"""
<header class="rp-head"><div class="wrap">
  <div class="crumb"><a href="../../">basil-saji</a> / <a href="../../#documents">documents</a> / {e(d["slug"])}</div>
  <span class="kind mono" style="color:var(--copper);font-size:.75rem;letter-spacing:.12em;text-transform:uppercase">{e(d["kind"])}</span>
  <h1>{e(d["title"])}</h1>
  <div class="rp-meta">{chips}</div>
  <div class="btns">
    <a class="btn primary" href="{pdf}" download>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12m0 0 5-5m-5 5-5-5M4 21h16"/></svg>Download PDF</a>
    <a class="btn" href="{pdf}" target="_blank" rel="noopener">Open original PDF</a>
    <button class="btn" data-copy>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>Copy link</button>
  </div>
</div></header>
<main class="wrap rp-body">
  <aside class="rp-side">
    <div class="card"><div class="label">Summary</div><p style="color:#c4d0db;font-size:.92rem">{e(d["summary"])}</p></div>
    <div class="card"><div class="label">Details</div><table class="ds-table">{facts}</table></div>
    {pts_card}
    <div class="btns">{rel}<a class="btn" href="../../#documents">← All documents</a></div>
  </aside>
  <div class="pages">
{figs}
  </div>
</main>
<footer><div class="wrap"><span>© Basil Saji · Electrical &amp; Electronics Engineer (Marine)</span><a href="../../" style="text-decoration:none">← Back to portfolio</a></div></footer>
<div class="toast">Link copied ✓</div>
<script src="../../assets/site.js"></script>
</body></html>
"""


if __name__ == "__main__":
    for d in DOCS:
        out = os.path.join(ROOT, "reports", d["slug"])
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
            f.write(page(d))
        print("reports/%s/" % d["slug"])
