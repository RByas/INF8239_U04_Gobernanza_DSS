import pandas as pd, pytest
from inf8239_u04.data import load_data
from inf8239_u04.governance import deployment_decision,load_config,trace,validate_raci
from inf8239_u04.pipeline import run
GATES={"min_recall":.7,"min_group_recall":.7,"min_group_size":30,"max_recall_gap":.2,"max_fpr_gap":.2,"max_latency_ms":10,"max_model_kb":20}
OK=({"recall_gap":.1,"fpr_gap":.1},{"latency_ms":1,"model_kb":5})
def test_failed_gate_requires_review():
    d=deployment_decision({"recall":.5},{"recall_gap":.1,"fpr_gap":.1},{"latency_ms":1,"model_kb":5},{"min_recall":.7,"max_recall_gap":.2,"max_fpr_gap":.2,"max_latency_ms":10,"max_model_kb":20}); assert d["status"]=="REVIEW"
def test_low_group_recall_requires_review_even_if_global_passes():
    m={"recall":.8,"group_recall":{"G1":{"recall":.6,"n":100},"G2":{"recall":.9,"n":60}}}
    d=deployment_decision(m,*OK,GATES); assert d["status"]=="REVIEW" and d["failed"]==["group_recall"]
def test_small_group_does_not_trigger_group_gate():
    m={"recall":.8,"group_recall":{"G1":{"recall":.9,"n":100},"G2":{"recall":.5,"n":10}}}
    assert deployment_decision(m,*OK,GATES)["status"]=="GO"
def test_privacy_breach_stops():
    d=deployment_decision({"recall":.8},*OK,GATES,privacy={"forbidden_in_features":["protected_group"]}); assert d["status"]=="STOP"
def test_raci_requires_accountable():
    with pytest.raises(ValueError): validate_raci(pd.DataFrame([{"activity":"deploy","R":"ML","A":"","C":"DS","I":"Users"}]))
def test_raci_rejects_shared_accountable():
    with pytest.raises(ValueError,match="one Accountable"): validate_raci(pd.DataFrame([{"activity":"deploy","R":"ML","A":"PO; Owner","C":"DS","I":"Users"}]))
def test_student_raci_is_valid():
    assert validate_raci(pd.read_csv("student_inputs/raci.csv"))
def test_governed_decision_is_review_with_trace():
    cfg=load_config(); d=run(load_data(),cfg["gates"],policy=cfg)["decision"]
    assert d["status"]=="REVIEW" and "group_recall" in d["failed"] and d["checks"]["privacy"]
    t=trace(evidence=["reports/lab12/AUDIT_REPORT.md"]); assert {"package_version","git_commit","policy","policy_sha256","evidence"}<=set(t)
