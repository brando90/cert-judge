# EXP21 Cert-Index Sweep

- source: `experiments/04_veribench_validation/results_exp16_final_robust_r9_median/summary.json`
- label set: `avg`
- baseline v1: rho=0.762, CI=[0.103, 1.000], width=0.897

## Best objective (rho - 0.25*CI_width)
- id=2043 arith comps=ident|mono|stab|weak w=0.200|0.400|0.400|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=3261 arith comps=ident|mono|stab|subtle|weak w=0.200|0.400|0.400|0.000|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=493 arith comps=ident|mono|stab w=0.200|0.400|0.400 | rho=0.881 CI=[0.385,1.000] width=0.615
- id=853 arith comps=anti|ident|mono|stab w=0.000|0.200|0.400|0.400 | rho=0.881 CI=[0.385,1.000] width=0.615
- id=1939 arith comps=ident|mono|stab|subtle w=0.200|0.400|0.400|0.000 | rho=0.881 CI=[0.385,1.000] width=0.615
- id=2449 arith comps=anti|ident|mono|stab|subtle w=0.000|0.200|0.400|0.400|0.000 | rho=0.881 CI=[0.383,1.000] width=0.617
- id=2651 arith comps=anti|ident|mono|stab|weak w=0.000|0.200|0.400|0.400|0.000 | rho=0.881 CI=[0.367,1.000] width=0.633
- id=3177 arith comps=anti|mono|stab|subtle|weak w=0.000|0.400|0.600|0.000|0.000 | rho=0.857 CI=[0.383,1.000] width=0.617
- id=1906 geom comps=ident|mono|stab|subtle w=0.000|0.400|0.600|0.000 | rho=0.857 CI=[0.367,1.000] width=0.633
- id=2015 arith comps=ident|mono|stab|weak w=0.000|0.600|0.400|0.000 | rho=0.857 CI=[0.367,1.000] width=0.633

## Candidates with rho >= min_rho (sorted by CI width)
- id=2043 arith comps=ident|mono|stab|weak w=0.200|0.400|0.400|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=3261 arith comps=ident|mono|stab|subtle|weak w=0.200|0.400|0.400|0.000|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=493 arith comps=ident|mono|stab w=0.200|0.400|0.400 | rho=0.881 CI=[0.385,1.000] width=0.615
- id=853 arith comps=anti|ident|mono|stab w=0.000|0.200|0.400|0.400 | rho=0.881 CI=[0.385,1.000] width=0.615
- id=1939 arith comps=ident|mono|stab|subtle w=0.200|0.400|0.400|0.000 | rho=0.881 CI=[0.385,1.000] width=0.615
- id=2449 arith comps=anti|ident|mono|stab|subtle w=0.000|0.200|0.400|0.400|0.000 | rho=0.881 CI=[0.383,1.000] width=0.617
- id=3177 arith comps=anti|mono|stab|subtle|weak w=0.000|0.400|0.600|0.000|0.000 | rho=0.857 CI=[0.383,1.000] width=0.617
- id=2651 arith comps=anti|ident|mono|stab|weak w=0.000|0.200|0.400|0.400|0.000 | rho=0.881 CI=[0.367,1.000] width=0.633
- id=1906 geom comps=ident|mono|stab|subtle w=0.000|0.400|0.600|0.000 | rho=0.857 CI=[0.367,1.000] width=0.633
- id=2015 arith comps=ident|mono|stab|weak w=0.000|0.600|0.400|0.000 | rho=0.857 CI=[0.367,1.000] width=0.633