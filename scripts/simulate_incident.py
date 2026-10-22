import json
from datetime import datetime,timezone
from pathlib import Path
from inf8239_u04.data import load_data
from inf8239_u04.governance import load_config,trace
from inf8239_u04.pipeline import run
# Simulacro: tras una actualización entra a producción el árbol en lugar del modelo logístico revisado.
# La señal no se declara: el modelo pasa por las mismas puertas y se registra lo que devuelven.
cfg=load_config(); df=load_data(); out=Path("reports/lab13"); out.mkdir(parents=True,exist_ok=True)
incident=run(df,cfg["gates"],kind="tree",policy=cfg); approved=run(df,cfg["gates"],kind="logistic",policy=cfg)
drill={"id":"INC-2026-001 (simulacro)","detected_at":datetime.now(timezone.utc).isoformat(timespec="seconds"),
  "scenario":"tree model deployed instead of the reviewed logistic model",
  "signal":{"status":incident["decision"]["status"],"failed":incident["decision"]["failed"],"gaps":incident["gaps"],"group_recall":incident["metrics"]["group_recall"]},
  "containment":"Institutional Owner suspends the ranking; queue falls back to FIFO with public rules (docs/RUNBOOK.md step 5)",
  "evidence":trace(kind="tree",evidence=["reports/lab13/incident_drill.json","reports/lab13/deployment_decision.json","reports/lab12/tree/global_metrics.json"]),
  "rollback_check":{"model":"logistic","status":approved["decision"]["status"],"failed":approved["decision"]["failed"],
    "note":"The reviewed model is not GO either (group_recall), so rollback goes to the FIFO baseline, not back to the logistic model"}}
(out/"incident_drill.json").write_text(json.dumps(drill,indent=2,ensure_ascii=False),encoding="utf-8")
post=out/"INCIDENT_POSTMORTEM.md"
if not post.exists(): post.write_text("# Incident postmortem\n\nREPLACE with timeline, communication, root cause and corrective actions (owner, date).\n",encoding="utf-8")
print(json.dumps(drill["signal"],indent=2)); print(out/"incident_drill.json")
