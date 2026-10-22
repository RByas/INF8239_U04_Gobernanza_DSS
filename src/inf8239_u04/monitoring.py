import pandas as pd

def _rate(y, p, positive):
    mask=y==positive
    return float(p[mask].mean()) if mask.any() else float("nan")

def monthly_monitor(test, pred, gates, freq="M"):
    # Mismas puertas que el despliegue, recalculadas por periodo; un grupo con n < min_group_size alerta como "revisar", no como falla
    df=test.assign(pred=pred,period=test.received_date.dt.to_period(freq).astype(str)); rows=[]
    for period,g in df.groupby("period"):
        row={"period":period,"n":len(g)}
        for grp,s in g.groupby("protected_group"):
            row[f"n_{grp}"]=len(s); row[f"recall_{grp}"]=_rate(s.target,s.pred,1); row[f"fpr_{grp}"]=_rate(s.target,s.pred,0)
        groups=sorted(g.protected_group.unique())
        row["recall_gap"]=max(row[f"recall_{k}"] for k in groups)-min(row[f"recall_{k}"] for k in groups)
        row["fpr_gap"]=max(row[f"fpr_{k}"] for k in groups)-min(row[f"fpr_{k}"] for k in groups)
        small=[k for k in groups if row[f"n_{k}"]<gates["min_group_size"]]
        alerts=[f"group_recall:{k}" for k in groups if k not in small and row[f"recall_{k}"]<gates["min_group_recall"]]
        if row["recall_gap"]>gates["max_recall_gap"]: alerts.append("recall_gap")
        if row["fpr_gap"]>gates["max_fpr_gap"]: alerts.append("fpr_gap")
        row["low_support"]=";".join(small); row["alerts"]=";".join(alerts)
        row["status"]="ALERT" if any(a.startswith("group_recall") for a in alerts) else "REVIEW" if alerts else "OK"
        if len(small)==len(groups): row["status"]="LOW_SUPPORT"
        rows.append(row)
    return pd.DataFrame(rows)
