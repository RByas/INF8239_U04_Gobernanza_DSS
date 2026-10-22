from pathlib import Path
from streamlit.testing.v1 import AppTest
def test_app_starts_and_discloses_synthetic_case():
    at=AppTest.from_file(Path(__file__).parents[1]/"app.py",default_timeout=20).run(); assert not at.exception; assert any("sintético" in x.value.lower() for x in at.warning)
    # La puerta fallida se muestra, no se oculta, y la salida incluye trazabilidad y acción humana
    assert any("REVIEW" in x.value for x in at.error); assert any("Trazabilidad" in x.value for x in at.subheader); assert any("Acción humana" in x.value for x in at.info)
