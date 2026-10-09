import json
from pathlib import Path
import numpy as np, pandas as pd
from inf8239_u04.data import load_data,features,temporal_split
from inf8239_u04.fairness import audit,intersectional,gap
from inf8239_u04.governance import load_config
from inf8239_u04.model import build_model
# Compara la alternativa no predictiva (reglas de lab11_impact.yml) con ambos modelos e
# incluye intervalos bootstrap (95%) de las brechas de recall y FPR entre G1 y G2.
cfg=load_config(); min_n=cfg["min_group_size"]; out=Path("reports/lab12"); out.mkdir(parents=True,exist_ok=True)
df=load_data(); train,test=temporal_split(df); y,g=test.target.to_numpy(),test.protected_group.to_numpy()
preds={"baseline_rules":((test.previous_incidents>=5)|(test.exposure>=0.7)).astype(int).to_numpy()}
for kind in ["logistic","tree"]: preds[kind]=build_model(kind).fit(features(train),train.target).predict(features(test))
def gaps(yt,yp,gr):
    _,bg,_=audit(yt,yp,gr); return gap(bg,"recall"),gap(bg,"fpr")
rng=np.random.default_rng(42); rows=[]; inter_rows=[]
for name,p in preds.items():
    overall,bg,_=audit(y,p,g); boot=[]
    for _ in range(500):
        i=rng.integers(0,len(y),len(y)); boot.append(gaps(y[i],p[i],g[i]))
    lo,hi=np.percentile(boot,[2.5,97.5],axis=0)
    rows.append({"model":name,"accuracy":overall.accuracy,"recall":overall.recall,"fpr":overall.fpr,"selection_rate":overall.selection_rate,
                 "recall_G1":bg.recall["G1"],"recall_G2":bg.recall["G2"],"fpr_G1":bg.fpr["G1"],"fpr_G2":bg.fpr["G2"],
                 "recall_gap":gap(bg,"recall"),"recall_gap_ci95":f"[{lo[0]:.3f}, {hi[0]:.3f}]","fpr_gap":gap(bg,"fpr"),"fpr_gap_ci95":f"[{lo[1]:.3f}, {hi[1]:.3f}]"})
    _,inter,_=audit(y,p,intersectional(test)); inter=inter.assign(model=name,sufficient_support=inter["count"]>=min_n); inter_rows.append(inter)
table=pd.DataFrame(rows); table.to_csv(out/"model_comparison.csv",index=False)
inter=pd.concat(inter_rows); inter.to_csv(out/"intersectional_support.csv")
(out/"support_warnings.json").write_text(json.dumps({"min_group_size":min_n,"insufficient_subgroups":sorted(inter.loc[~inter.sufficient_support].index.unique().tolist())},indent=2,ensure_ascii=False),encoding="utf-8")
print(table.round(3).to_string(index=False))
