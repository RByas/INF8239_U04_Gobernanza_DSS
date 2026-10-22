import json
from pathlib import Path
import pandas as pd
from inf8239_u04.data import load_data
from inf8239_u04.governance import load_config,trace,validate_raci
from inf8239_u04.pipeline import run
EVIDENCE=["reports/lab11/DECISION_RECORD.md","reports/lab12/AUDIT_REPORT.md","reports/lab12/logistic/bootstrap_ci.csv","reports/lab12/mitigation/threshold_strategies.csv","student_inputs/raci.csv"]
cfg=load_config(); validate_raci(pd.read_csv("student_inputs/raci.csv")); result=run(load_data(),cfg["gates"],policy=cfg)
out=Path("reports/lab13"); out.mkdir(parents=True,exist_ok=True)
(out/"deployment_decision.json").write_text(json.dumps({"trace":trace(kind="logistic",evidence=EVIDENCE),"metrics":result["metrics"],"gaps":result["gaps"],"resources":result["resources"],"privacy":result["privacy"],"decision":result["decision"]},indent=2,ensure_ascii=False),encoding="utf-8")
result["by_group"].to_csv(out/"fairness_by_group.csv"); print(result["decision"])
