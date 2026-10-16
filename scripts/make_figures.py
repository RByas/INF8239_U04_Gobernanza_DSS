import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
from inf8239_u04.data import load_data,features,temporal_split
from inf8239_u04.fairness import audit,gap
from inf8239_u04.governance import load_config
from inf8239_u04.pipeline import run
# Gráficos de evidencia para E07 (LAB12) y E08 (LAB13). Lee los CSV/JSON ya generados por
# lab12_compare.py, lab12_mitigation.py y lab13_governance.py; solo reentrena en la figura de
# puertas y en el monitoreo por mes. Uso: uv run --with matplotlib python scripts/make_figures.py
cfg=load_config(); gates=cfg["gates"]; min_n=cfg["min_group_size"]; min_rec=gates["min_recall"]
out=Path("docs/entregables/figs"); out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,"figure.dpi":150})
LABEL={"baseline_rules":"Reglas","logistic":"Logística","tree":"Árbol"}
C_G1,C_G2,C_BAD,C_OK,C_GREY="#1f77b4","#ff7f0e","#c0392b","#2e8b57","#b0b0b0"
def save(fig,name):
    fig.tight_layout(); fig.savefig(out/name,bbox_inches="tight"); plt.close(fig); print(out/name)

cmp=pd.read_csv("reports/lab12/model_comparison.csv")

# 1. Recall y FPR por grupo
fig,axes=plt.subplots(1,2,figsize=(9,3.2)); x=np.arange(len(cmp)); w=.36
for ax,m,title in [(axes[0],"recall","Recall por grupo"),(axes[1],"fpr","FPR por grupo")]:
    for off,gname,c in [(-w/2,"G1",C_G1),(w/2,"G2",C_G2)]:
        b=ax.bar(x+off,cmp[f"{m}_{gname}"],w,label=gname,color=c); ax.bar_label(b,fmt="%.3f",fontsize=7.5,padding=1)
    ax.set_xticks(x,[LABEL[k] for k in cmp.model]); ax.set_title(title); ax.set_ylim(0,1.05)
axes[0].axhline(min_rec,color=C_BAD,ls="--",lw=1); axes[0].text(-.45,min_rec+.02,f"mínimo {min_rec}",color=C_BAD,fontsize=7.5)
axes[0].legend(loc="upper left",fontsize=8); save(fig,"e07_recall_fpr_grupo.png")

# 2. Brechas con IC95
fig,axes=plt.subplots(1,2,figsize=(9,3.0),sharey=True)
for ax,m,title in [(axes[0],"recall","Brecha de recall G1–G2"),(axes[1],"fpr","Brecha de FPR G1–G2")]:
    lo,hi=zip(*[json.loads(s) for s in cmp[f"{m}_gap_ci95"]]); v=cmp[f"{m}_gap"].to_numpy()
    tol=gates[f"max_{m}_gap"]; colors=[C_BAD if g>tol else C_OK for g in v]
    ax.errorbar(x,v,yerr=[v-np.array(lo),np.array(hi)-v],fmt="none",ecolor="#555",capsize=4,lw=1)
    ax.scatter(x,v,c=colors,s=40,zorder=3)
    for i,val in enumerate(v): ax.text(i+.08,val,f"{val:.3f}",fontsize=7.5,va="center")
    ax.axhline(tol,color=C_BAD,ls="--",lw=1); ax.text(-.45,tol+.012,f"tolerancia {tol}",color=C_BAD,fontsize=7.5)
    ax.set_xticks(x,[LABEL[k] for k in cmp.model]); ax.set_title(title); ax.set_xlim(-.5,2.6)
axes[0].set_ylabel("Brecha (punto e IC95 bootstrap)"); save(fig,"e07_brechas_ic95.png")

# 3. Interseccional con soporte
inter=pd.read_csv("reports/lab12/intersectional_support.csv"); inter=inter[inter.model=="logistic"].reset_index(drop=True)
fig,ax=plt.subplots(figsize=(9,3.2)); xi=np.arange(len(inter))
colors=[(C_G1 if s.startswith("G1") else C_G2) if ok else C_GREY for s,ok in zip(inter.sensitive_feature_0,inter.sufficient_support)]
b=ax.bar(xi,inter.recall,color=colors,hatch=[None if ok else "//" for ok in inter.sufficient_support],edgecolor="white")
for i,r in inter.iterrows(): ax.text(i,r.recall+.02,f"{r.recall:.2f}\nn={int(r['count'])}",ha="center",fontsize=7.5,bbox=dict(fc="white",ec="none",pad=.5))
ax.axhline(min_rec,color=C_BAD,ls="--",lw=1); ax.set_ylim(0,1.25); ax.set_xticks(xi,inter.sensitive_feature_0,fontsize=8)
ax.set_ylabel("Recall (logística)"); ax.set_title(f"Recall interseccional · gris rayado = n < {min_n} (no se interpreta)")
save(fig,"e07_interseccional.png")

# 4. Mitigación: recall de G1 frente a FPR global
mit=pd.read_csv("reports/lab12/mitigation.csv")
NAMES={"logistic_threshold_0.5":"Umbral 0.5","logistic_threshold_0.45":"Umbral 0.45","logistic_threshold_0.4":"Umbral 0.4",
       "without_age_band":"Sin age_band","without_age_band_threshold_0.4":"Sin age_band + 0.4",
       "without_proxies":"Sin proxies","threshold_optimizer_equalized_odds":"ThresholdOptimizer"}
OFFS={"logistic_threshold_0.5":(6,5),"without_age_band":(-6,5)}
fig,ax=plt.subplots(figsize=(9,3.4))
for _,r in mit.iterrows():
    cand=r.variant=="logistic_threshold_0.4"; uses=r.uses_protected_group=="yes"
    ax.scatter(r.fpr,r.recall_G1,s=90 if cand else 45,marker="*" if cand else ("x" if uses else "o"),
               color=C_OK if cand else (C_BAD if uses else C_G1),zorder=3)
    ax.annotate(f"{NAMES[r.variant]} (brecha {r.recall_gap:.3f})",(r.fpr,r.recall_G1),xytext=OFFS.get(r.variant,(6,-3)),textcoords="offset points",fontsize=7.5,
                ha="right" if r.variant=="without_age_band" else "left")
ax.axhline(min_rec,color=C_BAD,ls="--",lw=1); ax.text(.185,min_rec+.008,f"recall mínimo {min_rec}",color=C_BAD,fontsize=7.5)
ax.set_xlabel("FPR global (costo: revisiones innecesarias)"); ax.set_ylabel("Recall de G1"); ax.set_xlim(.18,.62)
ax.set_title("Trade-off de mitigaciones · ★ candidata · × usa protected_group (prohibido)"); save(fig,"e07_mitigacion.png")

# 5. Puertas de calidad: logística aprobada frente a árbol (simulacro)
df=load_data(); res={k:run(df,gates,kind=k) for k in ["logistic","tree"]}
checks=[("Recall global","recall",lambda r:r["metrics"]["recall"],min_rec,True),
        ("Brecha recall","recall_gap",lambda r:r["gaps"]["recall_gap"],gates["max_recall_gap"],False),
        ("Brecha FPR","fpr_gap",lambda r:r["gaps"]["fpr_gap"],gates["max_fpr_gap"],False),
        ("Latencia (ms)","latency",lambda r:r["resources"]["latency_ms"],gates["max_latency_ms"],False),
        ("Tamaño (KB)","model_size",lambda r:r["resources"]["model_kb"],gates["max_model_kb"],False)]
fig,axes=plt.subplots(1,len(checks),figsize=(9,2.8))
for ax,(title,key,f,thr,higher) in zip(axes,checks):
    vals=[f(res[k]) for k in res]; cols=[C_OK if res[k]["decision"]["checks"][key] else C_BAD for k in res]
    b=ax.bar([LABEL[k] for k in res],vals,color=cols); ax.bar_label(b,fmt="%.3g",fontsize=7.5)
    ax.axhline(thr,color="#333",ls="--",lw=1); ax.set_title(f"{title}\n{'≥' if higher else '≤'} {thr}",fontsize=8.5)
    ax.tick_params(labelsize=7.5)
    if key in ("latency","model_size"): ax.set_yscale("log")
fig.suptitle(f"Puertas de calidad · Logística: {res['logistic']['decision']['status']} · Árbol: {res['tree']['decision']['status']} (verde = pasa, rojo = falla)",fontsize=9)
save(fig,"e08_puertas.png")

# 6. Monitoreo mensual de la brecha de recall (sep. se une a oct. por tener solo 6 casos)
test=res["logistic"]["test"]; month=test.received_date.dt.to_period("M").astype(str).replace({"2026-09":"2026-10"})
fig,axes=plt.subplots(1,2,figsize=(9,3.0))
for k,c,mk in [("logistic",C_G1,"o"),("tree",C_BAD,"s")]:
    pred=pd.Series(res[k]["pred"],index=test.index); rows=[]
    for mth,idx in test.groupby(month).groups.items():
        t=test.loc[idx]; _,bg,_=audit(t.target,pred.loc[idx],t.protected_group); rows.append((mth,gap(bg,"recall"),bg["recall"].get("G1",np.nan),len(t)))
    m=pd.DataFrame(rows,columns=["mes","gap","recall_g1","n"])
    axes[0].plot(m.mes,m.gap,marker=mk,color=c,label=LABEL[k]); axes[1].plot(m.mes,m.recall_g1,marker=mk,color=c,label=LABEL[k])
axes[0].axhline(gates["max_recall_gap"],color="#333",ls="--",lw=1); axes[0].set_title("Brecha de recall por mes (alerta > 0.16)")
axes[1].axhline(min_rec,color="#333",ls="--",lw=1); axes[1].set_title(f"Recall de G1 por mes (alerta < {min_rec})")
for ax in axes: ax.set_ylim(0,1); ax.legend(fontsize=8)
axes[0].set_xticks(range(len(m)),[f"{a}\nn={b}" for a,b in zip(m.mes,m.n)],fontsize=7.5); axes[1].set_xticks(range(len(m)),[f"{a}\nn={b}" for a,b in zip(m.mes,m.n)],fontsize=7.5)
save(fig,"e08_monitoreo.png")
