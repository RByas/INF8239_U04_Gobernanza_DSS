import csv, re, shutil, subprocess, sys
from pathlib import Path

# Genera docs/entregables/U04_E07_Sintesis_Roberto_Byas.pdf desde E07_sintesis.html.
# El gráfico se dibuja con los datos de reports/lab12/mitigation/threshold_strategies.csv.
# Formato: portada UASD, índice con páginas y cuerpo en Times New Roman 12, como el informe de referencia.
# Requiere Microsoft Edge (o Chrome) y PyMuPDF.
SRC=Path("docs/entregables/E07_sintesis.html"); OUT=Path("docs/entregables/U04_E07_Sintesis_Roberto_Byas.pdf")
RENDER=Path("docs/entregables/.E07_render.html")
LABELS={"A_":("A","Umbral base 0.50"),"B_":("B","Global 0.63"),"B2":("B2","Global con margen 0.30"),"C_":("C","Umbral por grupo"),"D_":("D","Fairlearn, paridad de recall")}
# Posición de cada etiqueta respecto de su punto: (dx, dy, anclaje)
PLACE={"A":(12,20,"start"),"B":(12,5,"start"),"B2":(-14,5,"end"),"C":(0,32,"middle"),"D":(14,5,"start")}
ACCENT,MUTED,INK,SOFT,GRID="#1f4e79","#9aa3ad","#000000","#404040","#d9d9d9"

def strategies():
    rows=[]
    for r in csv.DictReader(open("reports/lab12/mitigation/threshold_strategies.csv",encoding="utf-8")):
        key=next(k for k in ("B2","A_","B_","C_","D_") if r["strategy"].startswith(k))
        sid,name=LABELS[key]
        rows.append({"id":sid,"name":name,"reviews":float(r["reviews_per_100"]),"recall":float(r["recall_G1"]),"group":r["uses_protected_attribute"]=="True"})
    return rows

def chart(rows, lim=0.68):
    W,H,left,right,y0,bottom=760,330,64,730,24,280
    xs=lambda v:left+(v-40)/40*(right-left); ys=lambda v:bottom-(v-0.5)/0.5*(bottom-y0)
    s=[f"<svg viewBox='0 0 {W} {H}' xmlns='http://www.w3.org/2000/svg' font-family='Times New Roman, Times, serif' font-size='13'>"]
    for v in (0.5,0.6,0.7,0.8,0.9,1.0):
        s.append(f"<line x1='{left}' x2='{right}' y1='{ys(v):.1f}' y2='{ys(v):.1f}' stroke='{GRID}'/><text x='{left-8}' y='{ys(v)+4:.1f}' text-anchor='end' fill='{SOFT}'>{v:.1f}</text>")
    for v in (40,50,60,70,80):
        s.append(f"<text x='{xs(v):.1f}' y='{bottom+18}' text-anchor='middle' fill='{SOFT}'>{v}</text>")
    s.append(f"<line x1='{left}' x2='{right}' y1='{bottom}' y2='{bottom}' stroke='#8b95a3'/>")
    s.append(f"<text x='{right}' y='{bottom+40}' text-anchor='end' fill='{SOFT}'>Revisiones por cada 100 casos (carga del equipo)</text>")
    s.append(f"<text x='{left-8}' y='12' text-anchor='start' fill='{SOFT}'>Recall de G1</text>")
    s.append(f"<line x1='{left}' x2='{right}' y1='{ys(lim):.1f}' y2='{ys(lim):.1f}' stroke='#6b7686' stroke-dasharray='5 4'/><text x='{right}' y='{ys(lim)-6:.1f}' text-anchor='end' fill='{SOFT}'>Recall mínimo {lim}</text>")
    for r in rows:
        ok=r["recall"]>=lim; col=ACCENT if ok else MUTED; x,y=xs(r["reviews"]),ys(r["recall"]); dx,dy,anc=PLACE[r["id"]]
        fill="white" if r["group"] else col
        s.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='7' fill='{fill}' stroke='{col}' stroke-width='2.5'/>")
        s.append(f"<text x='{x+dx:.1f}' y='{y+dy:.1f}' text-anchor='{anc}' font-weight='700' fill='{INK if ok else SOFT}'>{r['id']} · {r['name']}</text>")
        s.append(f"<text x='{x+dx:.1f}' y='{y+dy+14:.1f}' text-anchor='{anc}' fill='{SOFT}'>{r['reviews']:.1f} rev. · recall {r['recall']:.3f}</text>")
    s.append("</svg>")
    return "".join(s)

def browser():
    for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
        if Path(p).exists(): return p
    return shutil.which("msedge") or shutil.which("google-chrome") or shutil.which("chromium") or sys.exit("No se encontró Edge ni Chrome")

def render(html):
    RENDER.write_text(html,encoding="utf-8")
    subprocess.run([browser(),"--headless","--disable-gpu","--no-pdf-header-footer",f"--print-to-pdf={OUT.resolve()}",RENDER.resolve().as_uri()],check=True,capture_output=True)
    RENDER.unlink()

def toc_pages(html):
    # Segunda pasada: busca cada título en el PDF (después del índice) y escribe su página en la tabla de contenido
    import pymupdf
    doc=pymupdf.open(OUT); texts=[" ".join(p.get_text().split()) for p in doc]; doc.close()
    for title in re.findall(r'data-toc="([^"]+)"',html):
        page=next((i+1 for i,t in enumerate(texts) if i>=2 and title in t),None)
        if page is None: sys.exit(f"Título no encontrado en el PDF: {title}")
        html=html.replace(f'data-toc="{title}">0<',f'data-toc="{title}">{page}<')
    return html

def number_pages(path):
    # Como en el formato de referencia: sin número en la portada ni en el índice; abajo a la derecha desde la página 3
    import pymupdf
    doc=pymupdf.open(path); tmp=path.with_suffix(".tmp.pdf")
    for i,page in enumerate(doc):
        if i<2: continue
        label=str(i+1); w,h=page.rect.width,page.rect.height
        page.insert_text((w-72-pymupdf.get_text_length(label,fontname="tiro",fontsize=11),h-40),label,fontname="tiro",fontsize=11)
    doc.save(tmp); doc.close(); tmp.replace(path)

try: import pymupdf  # noqa: F401
except ImportError: sys.exit("Instala PyMuPDF (pip install pymupdf): se usa para el índice y la numeración")
html=SRC.read_text(encoding="utf-8").replace("<!--CHART:mitigation-->",chart(strategies()))
render(html); render(toc_pages(html)); number_pages(OUT); print(OUT)
