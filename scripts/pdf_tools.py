import re, shutil, subprocess, sys
from pathlib import Path

# Herramientas comunes para las síntesis en formato UASD (portada, índice con páginas y Times New Roman 12).
# Requiere Microsoft Edge (o Chrome) y PyMuPDF.
ACCENT,MUTED,INK,SOFT,GRID="#1f4e79","#9aa3ad","#000000","#404040","#d9d9d9"

def browser():
    for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
        if Path(p).exists(): return p
    return shutil.which("msedge") or shutil.which("google-chrome") or shutil.which("chromium") or sys.exit("No se encontró Edge ni Chrome")

def _render(html, out, tmp):
    import tempfile, time
    tmp.write_text(html,encoding="utf-8"); out.unlink(missing_ok=True)
    # Perfil temporal: evita que Edge reutilice una página en caché o una instancia ya abierta
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:
        subprocess.run([browser(),"--headless","--disable-gpu","--no-first-run","--no-pdf-header-footer",f"--user-data-dir={profile}",f"--print-to-pdf={out.resolve()}",tmp.resolve().as_uri()],check=True,capture_output=True)
        # Edge puede regresar antes de terminar de escribir: se espera a que el PDF exista y deje de crecer
        last=-1
        for _ in range(120):
            size=out.stat().st_size if out.exists() else -1
            if size>0 and size==last: break
            last=size; time.sleep(0.5)
        else: sys.exit(f"Edge no generó {out}")
    tmp.unlink()

def _toc_pages(html, out):
    # Segunda pasada: busca cada título en el PDF (después del índice) y escribe su página en la tabla de contenido
    import pymupdf
    doc=pymupdf.open(out); texts=[" ".join(p.get_text().split()) for p in doc]; doc.close()
    for title in re.findall(r'data-toc="([^"]+)"',html):
        page=next((i+1 for i,t in enumerate(texts) if i>=2 and title in t),None)
        if page is None: sys.exit(f"Título no encontrado en el PDF: {title}")
        html=html.replace(f'data-toc="{title}">0<',f'data-toc="{title}">{page}<')
    return html

def _number_pages(out):
    # Sin número en la portada ni en el índice; abajo a la derecha desde la página 3
    import pymupdf
    doc=pymupdf.open(out); tmp=out.with_suffix(".tmp.pdf")
    for i,page in enumerate(doc):
        if i<2: continue
        label=str(i+1); w,h=page.rect.width,page.rect.height
        page.insert_text((w-72-pymupdf.get_text_length(label,fontname="tiro",fontsize=11),h-40),label,fontname="tiro",fontsize=11)
    doc.save(tmp); doc.close(); tmp.replace(out)

def build(src, out, charts):
    try: import pymupdf  # noqa: F401
    except ImportError: sys.exit("Instala PyMuPDF (pip install pymupdf): se usa para el índice y la numeración")
    src,out=Path(src),Path(out); html=src.read_text(encoding="utf-8")
    for marker,svg in charts.items(): html=html.replace(f"<!--CHART:{marker}-->",svg)
    tmp=src.with_name(f".{src.stem}_render.html")
    _render(html,out,tmp); _render(_toc_pages(html,out),out,tmp); _number_pages(out); print(out)

def svg_open(w, h):
    return f"<svg viewBox='0 0 {w} {h}' xmlns='http://www.w3.org/2000/svg' font-family='Times New Roman, Times, serif' font-size='13'>"
