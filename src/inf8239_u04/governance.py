from pathlib import Path
import pandas as pd
import yaml

def load_config(path="configs/governance.yml"):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def validate_raci(df):
    required={"activity","R","A","C","I"}
    if required-set(df.columns): raise ValueError("RACI columns missing")
    if df[["R","A"]].fillna("").apply(lambda s:s.str.strip().eq("")).any().any(): raise ValueError("Every activity needs R and A")
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

def deployment_decision(metrics, gaps, resources, gates):
    checks={
      "recall": metrics["recall"] >= gates["min_recall"],
      "recall_gap": gaps["recall_gap"] <= gates["max_recall_gap"],
      "fpr_gap": gaps["fpr_gap"] <= gates["max_fpr_gap"],
      "latency": resources["latency_ms"] <= gates["max_latency_ms"],
      "model_size": resources["model_kb"] <= gates["max_model_kb"],
    }
    failed=[k for k,v in checks.items() if not v]
    return {"status":"GO" if not failed else "REVIEW", "checks":checks, "failed":failed, "human_action":"Document review and final decision"}
