from pathlib import Path
import pandas as pd
from fairlearn.postprocessing import ThresholdOptimizer
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from inf8239_u04.data import load_data,features,temporal_split
from inf8239_u04.fairness import audit,gap
from inf8239_u04.model import build_model
# Mitigaciones candidatas sobre el baseline logistic: umbral global, quitar age_band (R03),
# quitar proxies (R02) y ThresholdOptimizer de Fairlearn (requiere protected_group al predecir).
df=load_data(); train,test=temporal_split(df); y,g=test.target,test.protected_group
def logistic(cat,num):
    prep=ColumnTransformer([("cat",OneHotEncoder(handle_unknown="ignore"),cat),("num",StandardScaler(),num)])
    return make_pipeline(prep,LogisticRegression(max_iter=1200,class_weight="balanced",random_state=42))
def row(name,pred,note):
    o,bg,_=audit(y,pred,g)
    return {"variant":name,"accuracy":o.accuracy,"recall":o.recall,"fpr":o.fpr,"recall_G1":bg.recall["G1"],"recall_G2":bg.recall["G2"],
            "recall_gap":gap(bg,"recall"),"fpr_gap":gap(bg,"fpr"),"uses_protected_group":note}
rows=[]; base=build_model("logistic").fit(features(train),train.target); proba=base.predict_proba(features(test))[:,1]
for t in [0.5,0.45,0.4]: rows.append(row(f"logistic_threshold_{t}",(proba>=t).astype(int),"no"))
num=["previous_incidents","infrastructure_score","exposure"]
m=logistic(["zone"],num).fit(train[["zone"]+num],train.target); rows.append(row("without_age_band",m.predict(test[["zone"]+num]),"no"))
rows.append(row("without_age_band_threshold_0.4",(m.predict_proba(test[["zone"]+num])[:,1]>=0.4).astype(int),"no"))
m=logistic(["zone","age_band"],["previous_incidents"]).fit(train[["zone","age_band","previous_incidents"]],train.target)
rows.append(row("without_proxies",m.predict(test[["zone","age_band","previous_incidents"]]),"no"))
to=ThresholdOptimizer(estimator=build_model("logistic"),constraints="equalized_odds",predict_method="predict_proba",prefit=False)
to.fit(features(train),train.target,sensitive_features=train.protected_group)
rows.append(row("threshold_optimizer_equalized_odds",to.predict(features(test),sensitive_features=g,random_state=42),"yes"))
out=pd.DataFrame(rows); Path("reports/lab12").mkdir(parents=True,exist_ok=True); out.to_csv("reports/lab12/mitigation.csv",index=False)
print(out.round(3).to_string(index=False))
