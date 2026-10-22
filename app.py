from pathlib import Path
import streamlit as st, yaml
from inf8239_u04.data import features, load_data
from inf8239_u04.governance import load_config, trace
from inf8239_u04.pipeline import run
st.set_page_config(page_title="Governed Green DSS",layout="wide")
st.title("DSS territorial sintético · Gobernanza y Green AI")
st.warning("Demostración educativa con datos sintéticos. No autoriza decisiones automáticas ni representa estadísticas reales.")
cfg=load_config(); result=run(load_data(),cfg["gates"],policy=cfg); decision=result["decision"]
st.subheader("Propósito y autoridad"); st.write(cfg["purpose"]); st.write("Usos prohibidos:",", ".join(cfg["prohibited_uses"]))
st.caption("El DSS prioriza la revisión y presenta evidencia. No declara emergencias, culpabilidad, elegibilidad ni intervención automática.")
c1,c2,c3=st.columns(3); c1.metric("Accuracy",f"{result['metrics']['accuracy']:.3f}"); c2.metric("Recall global",f"{result['metrics']['recall']:.3f}"); c3.metric("Recomendación",decision["status"])
st.subheader("Métricas por grupo"); st.dataframe(result["by_group"],use_container_width=True)
low=[g for g,r in result["metrics"]["group_recall"].items() if r["n"]>=cfg["gates"]["min_group_size"] and r["recall"]<cfg["gates"]["min_group_recall"]]
if low: st.error(f"Recall por debajo de {cfg['gates']['min_group_recall']} en: {', '.join(low)}. La puerta group_recall falla aunque el recall global cumpla.")
st.subheader("Puertas de calidad"); st.json({"checks":decision["checks"],"failed":decision["failed"]})
if decision["status"]!="GO": st.error(f"{decision['status']}: {decision['human_action']}")
st.subheader("Cola priorizada (salida del DSS)")
test=result["test"]; queue=test[["case_id","received_date","zone"]].assign(probability=result["model"].predict_proba(features(test))[:,1].round(3))
queue=queue.sort_values("probability",ascending=False).assign(priority=range(1,len(test)+1),action="Revisión humana; el operador decide")
st.dataframe(queue.head(20),use_container_width=True,hide_index=True)
st.subheader("Trazabilidad y decisión humana")
st.json(trace(kind="logistic",evidence=["reports/lab12/AUDIT_REPORT.md","reports/lab13/deployment_decision.json","docs/MODEL_CARD.md","docs/RUNBOOK.md"]))
human=yaml.safe_load(Path("student_inputs/lab12_decision.yml").read_text(encoding="utf-8"))
st.write("Decisión humana registrada:",human["recommendation"])
st.info("Acción humana: revisar evidencia, documentar la decisión y activar apelación o rollback cuando corresponda (docs/RUNBOOK.md).")
