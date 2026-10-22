import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
from inf8239_u04.data import load_data,features,temporal_split
from inf8239_u04.model import build_model
p=argparse.ArgumentParser(); p.add_argument("--model",choices=["logistic","tree"],default="logistic"); p.add_argument("--reps",type=int,default=2000); args=p.parse_args()
out=Path("reports/lab12")/args.model; out.mkdir(parents=True,exist_ok=True)
df=load_data(); train,test=temporal_split(df); model=build_model(args.model).fit(features(train),train.target)
y=test.target.to_numpy(); pred=model.predict(features(test)); g=test.protected_group.to_numpy()

def rates(y,p):
    pos,neg=y==1,y==0
    return (p[pos].mean() if pos.any() else np.nan),(p[neg].mean() if neg.any() else np.nan)

# Bootstrap estratificado: se remuestrea dentro de cada grupo para conservar su tamaño
rng=np.random.default_rng(42); idx={k:np.flatnonzero(g==k) for k in ("G1","G2")}; rows=[]
for _ in range(args.reps):
    r={}
    for k,i in idx.items():
        s=rng.choice(i,len(i)); r[k]=rates(y[s],pred[s])
    rows.append({"recall_G1":r["G1"][0],"recall_G2":r["G2"][0],"fpr_G1":r["G1"][1],"fpr_G2":r["G2"][1],
                 "recall_gap":abs(r["G2"][0]-r["G1"][0]),"fpr_gap":abs(r["G2"][1]-r["G1"][1])})
boot=pd.DataFrame(rows); point={k:rates(y[i],pred[i]) for k,i in idx.items()}
est={"recall_G1":point["G1"][0],"recall_G2":point["G2"][0],"fpr_G1":point["G1"][1],"fpr_G2":point["G2"][1],
     "recall_gap":abs(point["G2"][0]-point["G1"][0]),"fpr_gap":abs(point["G2"][1]-point["G1"][1])}
ci=pd.DataFrame({"estimate":est,"ci_low":boot.quantile(.025),"ci_high":boot.quantile(.975)})
ci["p_gap_above_0.16"]=[(boot[c]>.16).mean() if c.endswith("gap") else np.nan for c in ci.index]
ci["p_below_0.68"]=[(boot[c]<.68).mean() if c.startswith("recall_G") else np.nan for c in ci.index]
ci.to_csv(out/"bootstrap_ci.csv",index_label="metric")
(out/"bootstrap_meta.json").write_text(json.dumps({"reps":args.reps,"seed":42,"method":"percentile, stratified by protected_group","n_test":len(test)},indent=2),encoding="utf-8")
print(ci.round(3))
