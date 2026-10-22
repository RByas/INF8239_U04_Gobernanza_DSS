import pandas as pd
from inf8239_u04.monitoring import monthly_monitor
GATES={"min_group_recall":.68,"min_group_size":3,"max_recall_gap":.16,"max_fpr_gap":.16}
def frame(month, g1_pred):
    # 4 casos por grupo y mes: 2 positivos y 2 negativos; G2 siempre acierta
    rows=[(f"2026-{month}-01","G1",t,p) for t,p in zip([1,1,0,0],g1_pred)]+[(f"2026-{month}-01","G2",t,t) for t in [1,1,0,0]]
    df=pd.DataFrame(rows,columns=["received_date","protected_group","target","pred"]); df["received_date"]=pd.to_datetime(df.received_date); return df
def test_group_recall_drop_raises_alert_in_its_month():
    df=pd.concat([frame("10",[1,1,0,0]),frame("11",[1,0,0,0])],ignore_index=True)
    m=monthly_monitor(df.drop(columns="pred"),df.pred.to_numpy(),GATES).set_index("period")
    assert m.loc["2026-10","status"]=="OK" and m.loc["2026-11","status"]=="ALERT" and "group_recall:G1" in m.loc["2026-11","alerts"]
def test_small_groups_are_flagged_not_concluded():
    df=frame("10",[1,0,0,0]); m=monthly_monitor(df.drop(columns="pred"),df.pred.to_numpy(),{**GATES,"min_group_size":10})
    assert m.status.iloc[0]=="LOW_SUPPORT" and "group_recall" not in m.alerts.iloc[0]
