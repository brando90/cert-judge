# EXP21 Cert-Index Sweep

- source: `experiments/04_veribench_validation/results_exp16_final_robust/summary.json`
- label set: `avg`
- baseline v1: rho=0.881, CI=[0.385, 1.000], width=0.615

## Best objective (rho - 0.25*CI_width)
- id=71 arith comps=ident|weak w=0.800|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=267 arith comps=anti|mono|stab w=0.000|0.400|0.600 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=268 geom comps=anti|mono|stab w=0.000|0.400|0.600 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=653 arith comps=ident|stab|weak w=0.600|0.200|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=657 arith comps=ident|stab|weak w=0.800|0.000|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=693 arith comps=ident|subtle|weak w=0.800|0.000|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=721 arith comps=mono|stab|subtle w=0.400|0.600|0.000 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=757 arith comps=mono|stab|weak w=0.400|0.600|0.000 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=758 geom comps=mono|stab|weak w=0.400|0.600|0.000 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=1081 arith comps=anti|ident|mono|weak w=0.000|0.800|0.000|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385

## Candidates with rho >= min_rho (sorted by CI width)
- id=71 arith comps=ident|weak w=0.800|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=267 arith comps=anti|mono|stab w=0.000|0.400|0.600 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=268 geom comps=anti|mono|stab w=0.000|0.400|0.600 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=653 arith comps=ident|stab|weak w=0.600|0.200|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=657 arith comps=ident|stab|weak w=0.800|0.000|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=693 arith comps=ident|subtle|weak w=0.800|0.000|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=721 arith comps=mono|stab|subtle w=0.400|0.600|0.000 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=757 arith comps=mono|stab|weak w=0.400|0.600|0.000 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=758 geom comps=mono|stab|weak w=0.400|0.600|0.000 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=1081 arith comps=anti|ident|mono|weak w=0.000|0.800|0.000|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385