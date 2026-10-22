import json
from pathlib import Path
from inf8239_u04.data import load_data
from inf8239_u04.governance import load_config,trace
from inf8239_u04.monitoring import monthly_monitor
from inf8239_u04.pipeline import run
# Monitoreo mensual sobre el periodo posterior al entrenamiento (prueba temporal), con las puertas de configs/governance.yml
cfg=load_config(); result=run(load_data(),cfg["gates"],policy=cfg)
mon=monthly_monitor(result["test"],result["pred"],cfg["gates"])
out=Path("reports/lab13"); out.mkdir(parents=True,exist_ok=True); mon.round(4).to_csv(out/"monitoring_monthly.csv",index=False)
summary={"trace":trace(kind="logistic",evidence=["reports/lab13/monitoring_monthly.csv"]),"periods":len(mon),
  "status_by_period":dict(zip(mon.period,mon.status)),"alerts_by_period":dict(zip(mon.period,mon.alerts)),
  "action":"Any ALERT opens an incident per docs/RUNBOOK.md; LOW_SUPPORT periods are reviewed, not concluded"}
(out/"monitoring_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
print(mon[["period","n","n_G1","n_G2","recall_G1","recall_G2","recall_gap","fpr_gap","status","alerts","low_support"]].round(3).to_string(index=False))
