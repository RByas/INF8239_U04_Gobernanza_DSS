from pathlib import Path
import pandas as pd
import yaml

def load_config(path="configs/governance.yml"):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def validate_raci(df):
    required={"activity","R","A","C","I"}
    if required-set(df.columns): raise ValueError("RACI columns missing")
    if df[["R","A"]].fillna("").apply(lambda s:s.str.strip().eq("")).any().any(): raise ValueError("Every activity needs R and A")
    # Varios roles se separan con ";": se admiten en R, C e I, pero cada actividad tiene un solo Accountable
    shared=df[df.A.str.contains(r";|,| and ",regex=True)]
    if len(shared): raise ValueError(f"Exactly one Accountable per activity: {list(shared.activity)}")
    if df.activity.duplicated().any(): raise ValueError("Duplicated RACI activity")
    return True

RMF_FUNCTIONS={"GOVERN","MAP","MEASURE","MANAGE"}
RMF_STATUS={"verificado","documentado","pendiente LAB13"}

def validate_rmf_map(df, root="."):
    required={"function","subcategory","requirement","control","evidence","status","risk_ids"}
    if required-set(df.columns): raise ValueError("NIST map columns missing")
    if set(df.function)-RMF_FUNCTIONS or RMF_FUNCTIONS-set(df.function): raise ValueError("Every RMF function must appear and no other")
    if set(df.status)-RMF_STATUS: raise ValueError(f"Status must be one of {sorted(RMF_STATUS)}")
    if not df.apply(lambda r:r.subcategory.startswith(r.function+" "),axis=1).all(): raise ValueError("Subcategory must match its function")
    # Un control "verificado" debe apoyarse en evidencia que existe; un archivo existente no basta para marcarlo así
    missing=[(r.subcategory,p) for r in df.itertuples() if r.status!="pendiente LAB13" for p in r.evidence.split(";") if not (Path(root)/p).exists()]
    if missing: raise ValueError(f"Evidence not found: {missing}")
    return True

def rmf_summary(df):
    return {f:{"subcategories":list(g.subcategory),**g.status.value_counts().to_dict()} for f,g in df.groupby("function",sort=False)}

HUMAN_ACTION={
  "GO":"Product Owner reviews the evidence and signs the decision record before any use",
  "REVIEW":"Do not deploy: the accountable owner analyses the failed gates and records a decision (limit, modify or stop)",
  "STOP":"Do not deploy: privacy contract broken; Institutional Owner opens an incident per docs/RUNBOOK.md",
}

def deployment_decision(metrics, gaps, resources, gates, privacy=None):
    checks={
      "recall": metrics["recall"] >= gates["min_recall"],
      "recall_gap": gaps["recall_gap"] <= gates["max_recall_gap"],
      "fpr_gap": gaps["fpr_gap"] <= gates["max_fpr_gap"],
      "latency": resources["latency_ms"] <= gates["max_latency_ms"],
      "model_size": resources["model_kb"] <= gates["max_model_kb"],
    }
    # El recall global puede ocultar una falla localizada: cada grupo con soporte suficiente debe cumplir el mínimo
    if "min_group_recall" in gates and "group_recall" in metrics:
        checks["group_recall"]=all(r["recall"] >= gates["min_group_recall"] for r in metrics["group_recall"].values() if r["n"] >= gates.get("min_group_size",0))
    if privacy is not None: checks["privacy"]=not privacy["forbidden_in_features"]
    failed=[k for k,v in checks.items() if not v]
    status="STOP" if "privacy" in failed else "REVIEW" if failed else "GO"
    return {"status":status, "checks":checks, "failed":failed, "human_action":HUMAN_ACTION[status]}

def trace(policy_path="configs/governance.yml", kind="logistic", evidence=()):
    # Versión, política y evidencia que acompañan a cada recomendación
    import hashlib, subprocess
    from datetime import datetime, timezone
    from . import __version__
    try: commit=subprocess.run(["git","rev-parse","--short","HEAD"],capture_output=True,text=True,check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError): commit="unknown"
    return {"package_version":__version__,"git_commit":commit,"model":kind,"policy":policy_path,
            "policy_sha256":hashlib.sha256(Path(policy_path).read_bytes()).hexdigest()[:12],
            "evidence":list(evidence),"generated_at":datetime.now(timezone.utc).isoformat(timespec="seconds")}
