import json,glob,os,numpy as np
R="/var/lib/agent/scratch/e62/results/runs"
out=[]
for d in sorted(glob.glob(R+"/*/curves.json"))+[]:
    pass
for d in sorted(os.listdir(R)):
    p=f"{R}/{d}/FROZEN.json"
    if not os.path.exists(p) or d.startswith("arm1"): continue
    f=json.load(open(p)); c=f["curves"]
    tl=[e["train_loss"] for e in c["epochs"]]
    lg=[json.loads(l) for l in open(f"{R}/{d}/train_log.jsonl")]
    gn=[x["grad_norm"] for x in lg if "grad_norm" in x]; lr=[x["lr"] for x in lg if "lr" in x]
    out.append(dict(run=d,frozen_epoch=f["frozen_epoch"],selected_on=f["selected_on"],prior_ce=c["prior_ce"],train_loss_by_epoch=[round(t,3) for t in tl],
      val_teacher_start=round(c["start"]["val"]["rho_teacher"],3),val_teacher_by_epoch=[round(e["summary"]["val"]["rho_teacher"],3) for e in c["epochs"]],
      val_human_by_epoch=[round(e["summary"]["val"]["rho_human"],3) for e in c["epochs"]],val_mass_min=round(min(e["summary"]["val"]["mass"] for e in c["epochs"]),4),
      grad_norm=(round(min(gn),3),round(float(np.median(gn)),3),round(max(gn),3)) if gn else None,lr=(min(lr),max(lr)) if lr else None,n_log=len(lg),keys=sorted(lg[0].keys())))
json.dump(out,open("/var/lib/agent/scratch/e62/sanity.json","w"),indent=1)
for o in out: print(json.dumps(o)[:700])
print(json.load(open(R+"/sft_overfit/OVERFIT_TEST.json")))
