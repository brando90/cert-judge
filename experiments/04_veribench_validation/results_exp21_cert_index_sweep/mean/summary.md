# EXP21 Cert-Index Sweep

- source: `experiments/04_veribench_validation/results_exp16_final_robust/summary.json`
- label set: `avg`
- baseline v1: rho=0.881, CI=[0.385, 1.000], width=0.615

## Best objective (rho - 0.25*CI_width)
- id=159 arith comps=ident|weak w=0.800|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=169 arith comps=mono|stab w=0.400|0.600 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=782 geom comps=anti|mono|stab w=0.000|0.400|0.600 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=1536 geom comps=ident|mono|stab w=0.000|0.300|0.700 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=1539 arith comps=ident|mono|stab w=0.000|0.500|0.500 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=2083 arith comps=ident|stab|weak w=0.200|0.500|0.300 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=2145 arith comps=ident|stab|weak w=0.700|0.100|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=2371 arith comps=mono|stab|subtle w=0.400|0.600|0.000 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=2372 geom comps=mono|stab|subtle w=0.400|0.600|0.000 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=2497 arith comps=mono|stab|weak w=0.400|0.600|0.000 | rho=0.929 CI=[0.615,1.000] width=0.385

## Candidates with rho >= min_rho (sorted by CI width)
- id=159 arith comps=ident|weak w=0.800|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=169 arith comps=mono|stab w=0.400|0.600 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=782 geom comps=anti|mono|stab w=0.000|0.400|0.600 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=1536 geom comps=ident|mono|stab w=0.000|0.300|0.700 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=1539 arith comps=ident|mono|stab w=0.000|0.500|0.500 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=2083 arith comps=ident|stab|weak w=0.200|0.500|0.300 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=2145 arith comps=ident|stab|weak w=0.700|0.100|0.200 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=2371 arith comps=mono|stab|subtle w=0.400|0.600|0.000 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=2372 geom comps=mono|stab|subtle w=0.400|0.600|0.000 | rho=0.929 CI=[0.615,1.000] width=0.385
- id=2497 arith comps=mono|stab|weak w=0.400|0.600|0.000 | rho=0.929 CI=[0.615,1.000] width=0.385