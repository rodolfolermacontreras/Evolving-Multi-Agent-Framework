# Security Review -- Bridge Dashboard Live Azure Deployment

- **Reviewer:** Principal Cloud-Security Architect (active per ADR-0008)
- **Date:** 2026-05-16
- **Scope:** The live ACA deployment at https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io/
- **Status:** PASS with 4 recommended hardening steps (no blockers)

---

## TL;DR

The deployment is **secure for the stated threat model (single-user, low-traffic, MSDN-credit budget)**. All Easy Auth controls function as designed: unauthenticated requests cannot read application data, the allow-list reduces the population of accepted identities to one, and the container has no secrets to leak. There are four follow-up hardening steps below that would tighten the posture further but none block use.

---

## Identity (PASS)

| Check | Status | Evidence |
|-------|--------|----------|
| Authentication is required for application data | PASS | `GET /` returns 302 -> login.microsoftonline.com; `GET /healthz` also 302 (no info disclosure pre-auth) |
| Authentication uses Microsoft Entra ID, not local credentials | PASS | Easy Auth provider = azureactivedirectory; issuer = `https://login.microsoftonline.com/c6d3fc52-...../v2.0` |
| Token issuance flow correctly configured | PASS (after fix) | App reg `enableIdTokenIssuance=true` (LESSON-010 -- initial deploy missed this, fixed) |
| App registration audience is single-tenant | PASS | `signInAudience=AzureADMyOrg` -- restricts to the owner's personal Entra tenant only |
| Assignment-required gate is enforced | PASS | Enterprise app `appRoleAssignmentRequired=true` |
| Only the owner is assigned to the role | PASS | One assignment: Rodolfo Lerma (766b4806-...); no other principals |
| Container does not store or read any credentials | PASS | state_builder.py imports no auth libraries, reads no env-var secrets, writes no auth tokens to disk |
| No managed identity required for current functionality | PASS | The dashboard reads only the bundled repo; no Azure resource access from app code |

**Residual identity risk:** If the Entra tenant gains additional users in the future (it currently has one), assignment-required prevents them from accessing the dashboard unless they are also added to the Enterprise App. Documented in PROVISIONED.md teardown section.

## Network exposure (PASS)

| Check | Status | Evidence |
|-------|--------|----------|
| HTTPS enforced; HTTP rejected | PASS | ACA ingress transport=auto, all clients negotiate TLS 1.2+ |
| Auth required on EVERY route, including health | PASS | `/healthz` redirects to login -- no information disclosure to unauthenticated callers |
| No direct internet access to the container internal port | PASS | ACA ingress only exposes the FQDN; port 8080 is internal |
| External ingress confirmed required | PASS | Single-user remote-access goal requires public-internet-reachable FQDN; private endpoints would require VPN/Bastion which adds cost and complexity |
| TLS termination at platform edge | PASS | Managed by ACA; no app-side cert handling |
| Scale-to-zero limits idle attack surface | PASS | min=0, max=2; container literally not running when nobody is using it |
| Max-replica cap limits blast radius of resource exhaustion attacks | PASS | max=2 |

**Residual network risk:** A determined attacker can flood the public FQDN with unauthenticated requests, each triggering a redirect-to-login. Easy Auth handles these at the edge; cost impact bounded by free tier. Cost alert at $5 (deferred to portal step) provides early warning.

## Secret management (PASS)

| Check | Status | Evidence |
|-------|--------|----------|
| No secrets baked into container image | PASS | The image contains the repo (no `.env`, no credential files) |
| No secrets in environment variables on the Container App | PASS | `az containerapp show` reveals zero secret references |
| No secrets in ACA `secrets` config | PASS | None configured; none needed |
| Key Vault not in scope | N/A | Application has no secret-consuming code path |
| Container Registry credentials handled by managed identity (ACR pull) | PASS (auto) | `az containerapp up` configured this automatically when ACR was created |

**Residual secret risk:** None at current scope. If features that need secrets are added later, route through ACA `secrets` + env-var references (do NOT bake in image).

## Container image (PASS with recommendations)

| Check | Status | Evidence |
|-------|--------|----------|
| Image built reproducibly | PASS | `az containerapp up` used ACR Build; image SHA pinned per revision |
| Non-root container user | PASS | Dockerfile creates `app` user with UID 10001 and `USER app` |
| No package manager cache shipped | PASS | `rm -rf /var/lib/apt/lists/*` after apt-get install |
| Stdlib-only Python application | PASS | No `pip install` in Dockerfile (LESSON-001 honored) |
| Image SHA stored in revision history | PASS | Each `az containerapp update` records `image=...@sha256:...` |

**Recommended hardening (REC-1):** Pin the base image to a digest: `FROM python:3.13-slim@sha256:dc1546e...` instead of `FROM python:3.13-slim`. Prevents drift if Python rebuilds the slim tag with a regression or backdoor. Effort: trivial.

**Recommended hardening (REC-2):** Add a basic Content-Security-Policy header on responses. The dashboard currently serves inline CSS only; CSP would prevent injection if a future change accidentally pulls remote scripts. Effort: small (one response header in `state_builder.serve`).

## CI/CD posture (DEFERRED / PASS for manual deploys)

| Check | Status | Evidence |
|-------|--------|----------|
| Deploys via `az containerapp up --source .` from a trusted developer machine | PASS for v1 | Manual deploy; no automation surface |
| GitHub Actions OIDC federation NOT yet enabled | DEFERRED | Workflow YAML drafted in DESIGN.md §6, not committed |
| No long-lived service principal secret stored in GitHub | PASS | Manual-only deploys today |

**Recommended hardening (REC-3):** Before enabling automated CI/CD, commit the workflow file with OIDC federation only (no SP secret). The DESIGN.md §6 file is correct; just commit it disabled (workflow_dispatch only) and create the federated credential per the runbook step 5.

## Logging and audit (PASS)

| Check | Status | Evidence |
|-------|--------|----------|
| Container logs flow to Log Analytics | PASS (auto) | ACA auto-created a workspace and wired stdout/stderr |
| Sign-in audit lives in Entra ID logs | PASS | Sign-in events visible in Entra admin center -> Sign-in logs |
| Activity log captures resource changes | PASS | Azure Activity Log on the RG records every `az` mutation |
| 30-day retention is sufficient for single-user incident review | PASS | Default; tunable upward at small cost |

**Recommended hardening (REC-4):** Wire an Azure Monitor alert on Easy Auth failures (e.g. 10 failed sign-ins in 5 minutes from the same IP) to email the owner. Detects credential-stuffing attempts on the Entra app. Effort: small (one `az monitor metrics alert create`).

## Cost & abuse protection (PASS with portal step pending)

| Check | Status | Evidence |
|-------|--------|----------|
| Free-tier covers expected usage | PASS | 180k vCPU-sec + 360k GiB-sec + 2M requests/month free; single-user usage is ~1% of any of these |
| Hard cap on replicas | PASS | maxReplicas=2; bounds vCPU exhaustion attacks |
| Budget alert at $5/month | PORTAL STEP PENDING | CLI shorthand parser failed (documented); 30-second portal task |

## Compliance / data residency (PASS)

| Check | Status | Evidence |
|-------|--------|----------|
| No personal data stored at rest in this app | PASS | Application reads only Git artifacts; no DB writes; no PII |
| Deployment region matches user expectation | PASS | West US 2 (user is in PST timezone, default acceptable) |
| Sign-in logs are inside the user's own tenant | PASS | All Entra activity is in the user's personal tenant, not a third party |

## Threat model -- residuals

| Threat | Mitigation in place | Residual risk |
|--------|---------------------|---------------|
| Anonymous internet access reads dashboard | Easy Auth required on every route | None observed |
| Authorized but malicious tenant member accesses dashboard | Assignment required, only owner assigned | Tenant currently has only the owner; mitigation moot |
| Compromised GitHub account pushes poisoned image | Manual deploy only today; future: OIDC federation with branch lock | Repo owner is sole pusher; risk = account hygiene |
| Replay of stolen auth cookie | Easy Auth cookies are HttpOnly + Secure + SameSite-Lax | Time-bounded by ACA session token expiry (default 8 hours) |
| Resource exhaustion (cost attack) | scale-to-zero + max=2 + free tier headroom + $5 budget alert (pending) | <$5 burst, well under $10 ceiling |
| Future feature accidentally exposes API endpoint without auth | Auth is global (RequireAuth = globalValidation, not per-route opt-in) | New routes inherit auth gate by default |
| Token theft via XSS in the dashboard | Pure server-side HTML, no client-side JS today | If v2.1+ adds JS, must add CSP header (REC-2) |

## Final verdict

**APPROVED for production single-user use.**

The deployment passes all Cloud Adoption Framework "Secure" methodology checkpoints applicable to this scope. The four recommendations (REC-1 to REC-4) are hardening, not gating.

## Recommendations summary

| ID | Recommendation | Priority | Effort |
|----|----------------|----------|--------|
| REC-1 | Pin Python base image to a SHA digest in the Dockerfile | Medium | Trivial |
| REC-2 | Add a Content-Security-Policy response header (especially before SDD-008 adds JS) | Medium | Small |
| REC-3 | Commit the OIDC GH Actions workflow disabled (workflow_dispatch) + create the federated credential per runbook | Low | Small |
| REC-4 | Add Azure Monitor alert on >=10 failed Entra sign-ins in 5 minutes | Low | Small |
| REC-5 (PROVISIONED.md pending) | Set up $5/month budget alert via Portal | Low | 30 seconds in Portal |

None block ongoing use of the deployment.

## Sign-off

Principal Cloud-Security Architect, 2026-05-16. This review is valid until any of the following change: identity model, ingress configuration, image base, Easy Auth provider, role assignment scope, or container's secret-consumption pattern.
