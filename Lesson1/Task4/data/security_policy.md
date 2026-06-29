# NeuraStack Technologies — Security Policy

## Overview
This policy defines NeuraStack's security requirements for all employees, contractors, and systems. Compliance is mandatory. Violations must be reported to security@neurastack.io and may result in disciplinary action.

---

## 1. Password Policy

### Requirements
- Minimum password length: **12 characters**.
- Passwords must include at least: 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character (!@#$%^&*).
- Passwords must not contain the employee's name, email address, or the word "NeuraStack".
- Passwords must not reuse any of the last **10 passwords**.

### Rotation
- Passwords for all internal systems must be rotated every **90 days**.
- Employees are notified 14 days before password expiry.
- Accounts with expired passwords are locked after a 3-day grace period.

### Password Storage
- Passwords must never be stored in plaintext.
- Use **bcrypt** (cost factor 12) or **Argon2id** for password hashing.
- No passwords may be hardcoded in source code, configuration files, or scripts.

---

## 2. Multi-Factor Authentication (MFA)

- **MFA is mandatory** for all NeuraStack accounts: internal systems, cloud consoles, GitHub, and third-party SaaS tools.
- Approved MFA methods: Authenticator apps (Google Authenticator, Authy), hardware security keys (YubiKey).
- SMS-based MFA is **not approved** due to SIM-swap risks.
- MFA must be enabled within **48 hours** of account creation.

---

## 3. Data Classification

### Classification Levels
| Level | Description | Examples |
|---|---|---|
| **Public** | Safe for public disclosure | Marketing materials, public docs |
| **Internal** | For NeuraStack employees only | Internal wikis, meeting notes |
| **Confidential** | Sensitive business data | Customer data, financial reports, source code |
| **Restricted** | Highest sensitivity | API keys, credentials, PII, cryptographic keys |

### Handling Rules
- **Public:** No restrictions.
- **Internal:** Must not be shared externally without manager approval.
- **Confidential:** Encrypted at rest and in transit; access logged.
- **Restricted:** Zero-trust access only; must be stored in Azure Key Vault; access requires 2-person authorization.

---

## 4. Access Control

### Principle of Least Privilege
- Employees are granted the minimum permissions needed to perform their role.
- Access is reviewed quarterly by team leads and revoked when no longer needed.
- Temporary access (e.g., for incidents) must be revoked within 24 hours.

### Access Levels
| Level | Description |
|---|---|
| Read | View resources, no modification |
| Read/Write | Create and update resources |
| Admin | Full control including delete and permission management |
| Super Admin | Reserved for DevOps/Security team only |

### Offboarding
- All system access must be revoked within **2 hours** of an employee's last working day.
- Company devices must be returned and remotely wiped within **5 business days**.
- API keys issued to departing employees are immediately invalidated.

---

## 5. Secrets Management

- All secrets (API keys, database passwords, certificates) must be stored in **Azure Key Vault**.
- Secrets must never appear in:
  - Source code (git repositories)
  - Log files or monitoring dashboards
  - Slack, email, or other communication tools
  - `.env` files committed to version control (use `.env.example` with placeholder values)
- Secrets are rotated at least every **180 days** or immediately upon suspected compromise.
- The `detect-secrets` pre-commit hook is mandatory on all repositories to prevent accidental commits of secrets.

---

## 6. Network Security

- All data in transit must use **TLS 1.2 or higher**. TLS 1.0 and 1.1 are disabled.
- Internal services must communicate over the private **Azure VNet** — no public internet exposure.
- SSH access to production servers requires a **hardware security key** (YubiKey) and is limited to the DevOps team.
- VPN (Azure VPN Gateway) is required for accessing internal resources outside the office network.
- Port scanning or penetration testing against NeuraStack systems requires prior written approval from the Security team.

---

## 7. Incident Response

### Reporting
- Security incidents must be reported immediately to security@neurastack.io.
- All employees are obligated to report suspected incidents — "if in doubt, report it."
- Do not attempt to investigate or remediate a security incident independently.

### Breach Notification
- In the event of a confirmed data breach affecting customer data:
  - Affected customers are notified within **72 hours** (GDPR requirement).
  - Regulatory authorities are notified as required by applicable law.
  - A post-mortem is conducted within 14 days and shared internally.

---

## 8. Compliance

- NeuraStack complies with: **GDPR** (EU), **CCPA** (California), **SOC 2 Type II**.
- Annual third-party security audits are conducted each Q4.
- All employees complete mandatory security awareness training within 30 days of joining and annually thereafter.
