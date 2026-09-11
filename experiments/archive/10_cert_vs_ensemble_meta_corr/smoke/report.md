# Folder 10 Report (smoke)

- n_methods: 11
- Spearman(cert_v1, rho_human): -0.789
- Pearson(cert_v1, rho_human): -0.483

## Model A: rho ~ 1 + cert_v1
- beta_intercept = 5.1452 (se 2.9608)
- beta_cert_v1 = -5.4701 (se 3.3080)
- R^2 = 0.2330

## Model B: rho ~ 1 + cert_v1 + is_ensemble
- beta_intercept = 5.1434 (se 3.1382)
- beta_cert_v1 = -5.4721 (se 3.5062)
- beta_is_ensemble = 0.0097 (se 0.0906)
- R^2 = 0.2341
