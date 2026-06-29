# NeuraStack Technologies — Engineering Guidelines

## Overview
This document outlines NeuraStack's engineering processes, branching strategy, deployment rules, and operational standards for all software engineers.

---

## 1. Git Branching Strategy

NeuraStack follows a **trunk-based development** model with short-lived feature branches.

### Branch Types
| Branch | Pattern | Purpose |
|---|---|---|
| `main` | `main` | Production-ready code only. Direct pushes are blocked. |
| `develop` | `develop` | Integration branch for completed features. |
| Feature | `feature/<ticket-id>-<short-desc>` | New features or enhancements. |
| Bugfix | `bugfix/<ticket-id>-<short-desc>` | Bug fixes for develop branch. |
| Hotfix | `hotfix/<ticket-id>-<short-desc>` | Emergency fixes directly to production. |
| Release | `release/<version>` | Release stabilization (only bug fixes, no features). |

### Branch Rules
- Feature branches must be created from `develop`.
- Feature branches must be merged back into `develop` via Pull Request.
- Feature branches older than **2 weeks** are automatically flagged for cleanup.
- Hotfix branches are created from `main` and merged back into both `main` and `develop`.

---

## 2. Pull Request (PR) Process

### PR Requirements
- **Minimum 2 approvals** are required before merging any PR.
- At least 1 approver must be a senior engineer (L4 or above).
- All CI checks must pass (linting, tests, build) before merge is allowed.
- PRs with more than **500 lines changed** must be broken into smaller PRs.

### PR Title Format
```
[TYPE] Brief description of the change (Ticket: NS-1234)
```
Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`

Examples:
- `[feat] Add session-scoped file upload to NeuraChat (Ticket: NS-4521)`
- `[fix] Resolve null pointer in vector store search (Ticket: NS-4388)`

### PR Description Template
```
## What changed
Brief description of what was changed and why.

## How to test
Steps to verify the change works correctly.

## Checklist
- [ ] Unit tests added
- [ ] No secrets in code
- [ ] Docs updated (if applicable)
```

### PR Review SLA
- Reviewers must respond within **24 hours** on business days.
- PRs open for more than **5 days** without review are escalated to the team lead.

---

## 3. CI/CD Pipeline

### Pipeline Stages (in order)
1. **Lint** — ESLint (TypeScript) / Ruff (Python). Fail = block merge.
2. **Unit Tests** — pytest / Jest. Must achieve ≥ 80% coverage. Fail = block merge.
3. **Build** — Docker image build. Fail = block merge.
4. **Integration Tests** — Run against staging environment. Fail = block merge.
5. **Security Scan** — Trivy for container vulnerabilities, Bandit for Python. High severity = block merge.
6. **Deploy to Staging** — Automatic on merge to `develop`.
7. **Deploy to Production** — Manual approval required; automatic on merge to `main` after approval.

### Deployment Windows
- Production deployments are only allowed **Monday to Thursday, 10:00 AM – 3:00 PM CST**.
- No deployments allowed on Fridays or the day before a public holiday.
- Emergency hotfixes may bypass the window with VP Engineering approval.

---

## 4. Release Process

### Release Cadence
- NeuraStack ships **bi-weekly releases** on Tuesdays.
- Release versions follow **Semantic Versioning**: `MAJOR.MINOR.PATCH` (e.g., `2.4.1`).
  - MAJOR: Breaking API changes.
  - MINOR: New features, backwards-compatible.
  - PATCH: Bug fixes and patches.

### Release Steps
1. Create `release/vX.Y.Z` branch from `develop`.
2. Only bug fixes are allowed on release branches — no new features.
3. QA team runs regression tests (minimum 2 business days).
4. Merge to `main` and tag: `git tag v2.4.1`.
5. Deploy to production during the deployment window.
6. Merge release branch back into `develop`.
7. Publish release notes to Slack `#releases` channel.

---

## 5. Incident Response

### Severity Levels
| Level | Description | Response Time | Escalation |
|---|---|---|---|
| P1 — Critical | Full service outage or data loss | 15 minutes | CTO + VP Eng |
| P2 — High | Major feature broken, no workaround | 1 hour | Team Lead |
| P3 — Medium | Feature degraded, workaround exists | 4 hours | Engineer |
| P4 — Low | Minor UI bug or cosmetic issue | Next sprint | Backlog |

### On-Call Rotation
- Engineers rotate on-call weekly.
- On-call hours: 24/7 for P1 and P2; business hours only for P3 and P4.
- On-call engineers receive a **$200/week on-call stipend**.
- PagerDuty is used for alerting and escalation.

---

## 6. Code Ownership
- Each service has a designated **code owner** in the `CODEOWNERS` file.
- Code owners must be one of the PR approvers for changes to their service.
- Code ownership is reviewed and updated every quarter.

---

## 7. Documentation Standards
- All services must maintain an up-to-date `README.md` with: setup instructions, environment variables, and API endpoints.
- Architecture Decision Records (ADRs) are stored in `docs/adr/` and must be created for any significant technical decision.
- API documentation is auto-generated from OpenAPI specs using Swagger UI.
