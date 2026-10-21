# Search Judge lifecycle email receipts

**TLDR:** The authorized START email was sent; completion notification is pending the deterministic smoke outcome.

| Sent / attempted | Subject | Recipient routing | Verification |
|---|---|---|---|
| 10-21-2026 08:27 PDT | `[RUN START] cert-judge Search Judge smoke: already running` | To `brando.science@gmail.com`; BCC `brando.science@gmail.com`, `brando9@stanford.edu`, `brandojazz@gmail.com`, `brando@vals.ai`; no visible CC | `uutils.emailing.send_email_smtp` returned normally and emitted `SEND_OK`; SMTP accepted the message. |
| 10-21-2026 08:39 PDT | `[RUN DONE] cert-judge Search Judge smoke: success` | To `brando.science@gmail.com`; BCC `brando.science@gmail.com`, `brando9@stanford.edu`, `brandojazz@gmail.com`, `brando@vals.ai`; no visible CC | `uutils.emailing.send_email_smtp` returned normally and emitted `SEND_OK`; SMTP accepted the message. |
