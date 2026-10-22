import csv
import yaml
from pdf_tools import ACCENT,GRID,INK,MUTED,SOFT,build,svg_open

# Genera docs/entregables/U04_E08_Sintesis_Roberto_Byas.pdf desde E08_sintesis.html.
# El gráfico se dibuja con reports/lab13/monitoring_monthly.csv (scripts/lab13_monitor.py).
COLORS={"G1":ACCENT,"G2":MUTED}

def chart():
    gates=yaml.safe_load(open("configs/governance.yml",encoding="utf-8"))["gates"]; lim,min_n=gates["min_group_recall"],gates["min_group_size"]
    rows=list(csv.DictReader(open("reports/lab13/monitoring_monthly.csv",encoding="utf-8")))
    left,right,y0,bottom=64,600,24,250
    xs=lambda i:left+40+i*(right-left-80)/(len(rows)-1); ys=lambda v:bottom-(v-0.5)/0.5*(bottom-y0)
    s=[svg_open(760,300)]
    for v in (0.5,0.6,0.7,0.8,0.9,1.0):
        s.append(f"<line x1='{left}' x2='{right}' y1='{ys(v):.1f}' y2='{ys(v):.1f}' stroke='{GRID}'/><text x='{left-8}' y='{ys(v)+4:.1f}' text-anchor='end' fill='{SOFT}'>{v:.1f}</text>")
    s.append(f"<line x1='{left}' x2='{right}' y1='{bottom}' y2='{bottom}' stroke='#8b95a3'/>")
    s.append(f"<text x='{left-8}' y='12' text-anchor='start' fill='{SOFT}'>Recall por grupo</text>")
    s.append(f"<line x1='{left}' x2='{right}' y1='{ys(lim):.1f}' y2='{ys(lim):.1f}' stroke='#6b7686' stroke-dasharray='5 4'/><text x='{right+8}' y='{ys(lim)+4:.1f}' fill='{SOFT}'>Mínimo {lim}</text>")
    for i,r in enumerate(rows):
        s.append(f"<text x='{xs(i):.1f}' y='{bottom+18}' text-anchor='middle' fill='{INK}'>{r['period']}</text><text x='{xs(i):.1f}' y='{bottom+34}' text-anchor='middle' fill='{SOFT}' font-size='11'>n = {r['n']} · {r['status']}</text>")
    for g,col in COLORS.items():
        pts=[(xs(i),ys(float(r[f'recall_{g}']))) for i,r in enumerate(rows)]
        s.append(f"<polyline fill='none' stroke='{col}' stroke-width='2.5' points='{' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)}'/>")
        for (x,y),r in zip(pts,rows):
            small=int(r[f"n_{g}"])<min_n
            s.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='5.5' fill='{'white' if small else col}' stroke='{col}' stroke-width='2'/>")
        lx,ly=pts[-1]; s.append(f"<text x='{lx+12:.1f}' y='{ly+4:.1f}' font-weight='700' fill='{col if g=='G1' else SOFT}'>{g}</text>")
    s.append(f"<text x='{right+8}' y='{y0+10}' fill='{SOFT}' font-size='11'>○ hueco: n &lt; {min_n}</text>")
    s.append("</svg>")
    return "".join(s)

build("docs/entregables/E08_sintesis.html","docs/entregables/U04_E08_Sintesis_Roberto_Byas.pdf",{"monitoring":chart()})
