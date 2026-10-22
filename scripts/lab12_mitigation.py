import json
from pathlib import Path
import numpy as np, pandas as pd
from fairlearn.postprocessing import ThresholdOptimizer
from inf8239_u04.data import load_data,features,temporal_split
from inf8239_u04.model import build_model

# Los umbrales se eligen en una validación temporal (último 25 % del entrenamiento), nunca con la prueba
MIN_RECALL=.68; GRID=np.round(np.arange(.20,.71,.01),2); REPS=2000
out=Path("reports/lab12/mitigation"); out.mkdir(parents=True,exist_ok=True)
train,test=temporal_split(load_data()); fit,val=temporal_split(train)
sel_model=build_model().fit(features(fit),fit.target); p_val=sel_model.predict_proba(features(val))[:,1]
model=build_model().fit(features(train),train.target); p_test=model.predict_proba(features(test))[:,1]
y,g=test.target.to_numpy(),test.protected_group.to_numpy()
sub45=(g=="G1")&(test.age_band.to_numpy()=="45-59")  # único subgrupo interseccional con n ≥ 30

def rates(y,p):
    return p[y==1].mean(),p[y==0].mean()

def highest(mask_fn):
    # Umbral más alto (menos alertas) que alcanza el recall mínimo en validación
    ok=[t for t in GRID if mask_fn(t)]
    return max(ok) if ok else min(GRID)

yv,gv=val.target.to_numpy(),val.protected_group.to_numpy()
t_global=highest(lambda t:all(rates(yv[gv==k],(p_val[gv==k]>=t).astype(int))[0]>=MIN_RECALL for k in ("G1","G2")))
# Margen = semiamplitud del IC 95 % bootstrap del recall de G1 (lab12_bootstrap.py), fijado antes de mirar la prueba
ci=pd.read_csv("reports/lab12/logistic/bootstrap_ci.csv",index_col=0).loc["recall_G1"]; MARGIN=round((ci.ci_high-ci.ci_low)/2,3)
t_margin=highest(lambda t:all(rates(yv[gv==k],(p_val[gv==k]>=t).astype(int))[0]>=MIN_RECALL+MARGIN for k in ("G1","G2")))
t_group={k:highest(lambda t,k=k:rates(yv[gv==k],(p_val[gv==k]>=t).astype(int))[0]>=MIN_RECALL) for k in ("G1","G2")}
to=ThresholdOptimizer(estimator=sel_model,constraints="true_positive_rate_parity",objective="balanced_accuracy_score",prefit=True,predict_method="predict_proba")
to.fit(features(val),yv,sensitive_features=gv)
to.estimator_=model  # se aplica la regla aprendida sobre el modelo final

strategies={
  "A_baseline_0.50":(p_test>=.5).astype(int),
  f"B_global_{t_global:.2f}":(p_test>=t_global).astype(int),
  f"B2_global_margen_{t_margin:.2f}":(p_test>=t_margin).astype(int),
  f"C_por_grupo_G1_{t_group['G1']:.2f}_G2_{t_group['G2']:.2f}":np.where(g=="G1",p_test>=t_group["G1"],p_test>=t_group["G2"]).astype(int),
  "D_fairlearn_TPR_parity":to.predict(features(test),sensitive_features=g,random_state=42).astype(int),
}

def summary(pred,idx=None):
    r={}
    for k in ("G1","G2"):
        i=np.flatnonzero(g==k) if idx is None else idx[k]
        r[k]=(*rates(y[i],pred[i]),pred[i].mean())
    return r

rng=np.random.default_rng(42); idx={k:np.flatnonzero(g==k) for k in ("G1","G2")}
boots=[{k:rng.choice(i,len(i)) for k,i in idx.items()} for _ in range(REPS)]
rows=[]
for name,pred in strategies.items():
    s=summary(pred); tp=((pred==1)&(y==1)).sum()
    b=[summary(pred,bi) for bi in boots]
    rows.append({"strategy":name,"uses_protected_attribute":name[0] in "CD",
      "accuracy":(pred==y).mean(),"recall":pred[y==1].mean(),"fpr":pred[y==0].mean(),"precision":tp/max(pred.sum(),1),
      "selection_rate":pred.mean(),"reviews_per_100":pred.mean()*100,
      "recall_G1":s["G1"][0],"recall_G2":s["G2"][0],"fpr_G1":s["G1"][1],"fpr_G2":s["G2"][1],
      "recall_G1_45-59":pred[sub45&(y==1)].mean(),"fpr_G1_45-59":pred[sub45&(y==0)].mean(),
      "recall_gap":abs(s["G2"][0]-s["G1"][0]),"fpr_gap":abs(s["G2"][1]-s["G1"][1]),
      "p_recall_G1_below_0.68":np.mean([x["G1"][0]<MIN_RECALL for x in b]),
      "p_recall_gap_above_0.16":np.mean([abs(x["G2"][0]-x["G1"][0])>.16 for x in b]),
      "p_fpr_gap_above_0.16":np.mean([abs(x["G2"][1]-x["G1"][1])>.16 for x in b])})
res=pd.DataFrame(rows); res.to_csv(out/"threshold_strategies.csv",index=False)

# Curva descriptiva sobre la prueba: muestra el compromiso, no se usa para elegir el umbral
curve=[]
for t in GRID:
    pred=(p_test>=t).astype(int); s=summary(pred)
    curve.append({"threshold":t,"recall":pred[y==1].mean(),"fpr":pred[y==0].mean(),"selection_rate":pred.mean(),
      "recall_G1":s["G1"][0],"recall_G2":s["G2"][0],"fpr_G1":s["G1"][1],"fpr_G2":s["G2"][1]})
pd.DataFrame(curve).to_csv(out/"threshold_curve_test.csv",index=False)
(out/"mitigation_meta.json").write_text(json.dumps({"min_recall":MIN_RECALL,"grid":[float(GRID[0]),float(GRID[-1]),0.01],
  "selection_split":{"fit":len(fit),"validation":len(val)},"test":len(test),"bootstrap_reps":REPS,"seed":42,
  "t_global":float(t_global),"margin":float(MARGIN),"t_margin":float(t_margin),"t_group":{k:float(v) for k,v in t_group.items()}},indent=2),encoding="utf-8")
print(res.drop(columns=["uses_protected_attribute"]).set_index("strategy").T.round(3).to_string())
