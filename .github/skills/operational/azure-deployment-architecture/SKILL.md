---
name: azure-deployment-architecture
description: Reference patterns for deploying the framework's user-facing surfaces to Microsoft Azure with security-first defaults. Use when proposing or reviewing any Azure deployment for this project. Owned by principal-cloud-security-architect.
license: MIT
argument-hint: none -- this skill is always active when speaking as the Cloud Security Architect
metadata:
  author: emf-framework
  version: '1.0'
  origin: SDD-007 cloud-dashboard design exploration (2026-05-16)
---

# Azure Deployment Architecture (Security-First)

This skill encodes the default Azure deployment pattern for this project. The
canonical use case is: "single user, low traffic, secure, near-zero cost".

---

## The default pattern

**Azure Container Apps (Consumption plan) + Microsoft Entra ID built-in auth + scale-to-zero.**

Why this and not alternatives:

| Alternative | Why we did not pick it |
|-------------|------------------------|
| App Service B1 + Easy Auth | ~$13/mo flat even when idle; no scale-to-zero |
| Azure Functions + Static Web Apps | Dashboard is a long-lived HTTP process, not function-shaped |
| Azure VM | Patching overhead, no managed auth |
| AKS | Massive overkill for one container |

ACA Consumption gives us: free tier (180k vCPU-sec + 360k GiB-sec + 2M req per
subscription per month), scale-to-zero (`minReplicas=0`), built-in HTTPS, built-in
Microsoft Entra ID auth, container image from any registry.

## Security defaults (always applied)

1. **Ingress**: external=true, transport=auto, allow only HTTPS (ACA enforces TLS 1.2+).
2. **Auth**: Microsoft Entra ID built-in provider, "Require authentication" = true,
   "Unauthenticated requests" = "Redirect to login (302)", allowed audience =
   only the project owner's Entra tenant + a single allowed account email.
3. **Identity**: container uses a system-assigned managed identity. No client
   secrets. The MI is the only principal that can read from Key Vault if used.
4. **Secrets**: declare as ACA secrets (encrypted at rest, never logged) and
   reference via env vars; do NOT bake into the container image.
5. **Network**: in v1, public ingress with Entra auth = secure enough. If
   tightening is needed, move to a Container Apps Environment with VNet
   integration and restrict ingress to a private endpoint.
6. **Logging**: send container stdout/stderr to a Log Analytics workspace,
   30-day retention (free tier).
7. **Image source**: prefer GitHub Container Registry (ghcr.io) for free private
   images; otherwise Azure Container Registry Basic ($5/mo).
8. **Image hygiene**: pinned base image SHA (not `:latest`), non-root user,
   minimal layers, no apt cache.
9. **CI/CD**: deploy only via GitHub Actions using OIDC federated credentials
   (no service principal secrets stored in GitHub secrets); GitHub repo is
   federated to the Entra app registration that has only the minimum
   `Microsoft.App/containerApps/revisions/write` role on the target RG.

## Threat model template

When recommending an architecture, populate this table:

| Threat | Control | Residual risk |
|--------|---------|---------------|
| Unauthenticated access | Entra auth required, single-tenant audience | Other Entra users in same tenant could authenticate but are denied by allowed-user filter |
| Compromised image | Image signed via GitHub Actions OIDC; pinned base image SHA | If GitHub account compromised, attacker can publish a malicious image |
| Secret leakage | Secrets in ACA secret refs; managed identity for Key Vault | Logs could leak secret values if app logs them; mitigated by code review |
| DoS / billing attack | ACA scale-to-zero + free tier covers single-user traffic; cap maxReplicas=2 | A determined attacker could exhaust the free tier; mitigation: add cost alert at $5/mo |
| Token theft | Auth cookies are http-only and Secure flagged by ACA Easy Auth | Browser exploit on the user's device |

## Cost ceiling

This project's default cost ceiling is $10/month. Any architecture that exceeds
that under expected usage requires explicit human approval as a Level-2 decision
and an ADR.

## Standard runbook structure

When you write a deployment runbook, follow this exact section order:

1. **Prerequisites** (user must have): `az` CLI installed, `az login`, GitHub repo
   admin access.
2. **Create resource group** (one `az group create` command).
3. **Create Log Analytics workspace + Container Apps Environment.**
4. **Create the Entra app registration for auth + federated credential for CI/CD.**
   **CRITICAL: always pair `az ad app create` with `az ad app update --enable-id-token-issuance true`.**
   Easy Auth uses implicit flow with `response_type=id_token`; without id_token
   issuance enabled on the app reg, sign-in completes but ACA returns 401 post-auth
   (LESSON-010, learned the hard way 2026-05-16).
5. **Create the Container App** with min/max replicas, ingress, auth, secrets.
6. **Verify**: open the URL, expect a Microsoft login prompt.
7. **Tear down**: `az group delete` removes everything.

Every step must include the exact `az` command, expected output, and what to
do if it fails.

## Anti-patterns this skill exists to prevent

- "Just deploy it as an App Service" without explaining why scale-to-zero matters.
- Storing service principal secrets in GitHub repo secrets when OIDC federation works.
- Public ACA ingress with no auth "just for now".
- Baking secrets into container images.
- Using `:latest` tag in production deployments.
- Skipping the threat model because "it's just for me".
