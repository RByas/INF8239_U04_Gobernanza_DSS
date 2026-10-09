from pathlib import Path
import streamlit as st, yaml
from inf8239_u04 import __version__
from inf8239_u04.data import load_data
from inf8239_u04.governance import load_config
from inf8239_u04.pipeline import run
st.set_page_config(page_title="Governed Green DSS",layout="wide")
st.title("DSS territorial sintético · Gobernanza y Green AI")
st.warning("Demostración educativa con datos sintéticos. No autoriza decisiones automáticas ni representa estadísticas reales.")
cfg=load_config(); result=run(load_data(),cfg["gates"])
st.subheader("Propósito y autoridad"); st.write(cfg["purpose"]); st.write("Usos prohibidos:",", ".join(cfg["prohibited_uses"]))
c1,c2,c3=st.columns(3); c1.metric("Accuracy",f"{result['metrics']['accuracy']:.3f}"); c2.metric("Recall",f"{result['metrics']['recall']:.3f}"); c3.metric("Decisión",result["decision"]["status"])
st.subheader("Métricas por grupo"); st.dataframe(result["by_group"],use_container_width=True)
low=[g for g,r in result["by_group"].iterrows() if r["count"]>=cfg["min_group_size"] and r["recall"]<cfg["gates"]["min_recall"]]
if low: st.error(f"Recall por debajo de {cfg['gates']['min_recall']} en: {', '.join(low)}. El estado automático no lo refleja.")
st.subheader("Puertas de calidad"); st.json(result["decision"])
human=yaml.safe_load(Path("student_inputs/lab12_decision.yml").read_text(encoding="utf-8"))
st.subheader("Trazabilidad y decisión humana")
st.write(f"Versión: inf8239_u04 {__version__} · modelo logistic · política: configs/governance.yml · evidencia: reports/lab12/AUDIT_REPORT.md, reports/lab13/deployment_decision.json")
st.write("Decisión humana registrada:",human["recommendation"])
st.info("Acción humana: revisar evidencia, documentar la decisión y activar apelación o rollback cuando corresponda.")
