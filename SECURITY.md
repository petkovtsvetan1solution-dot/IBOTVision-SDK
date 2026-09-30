# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest release | ✅ |
| Previous minor | ✅ |
| Older versions | ❌ |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report security issues by email to: **security@ibotvision.com**

Include in your report:
- Description of the vulnerability and its potential impact
- Steps to reproduce (proof-of-concept code if available)
- Affected SDK version(s)
- Your suggested fix (optional)

## Response Timeline

| Stage | Target |
|-------|--------|
| Initial acknowledgement | 72 hours |
| Confirmed / triaged | 7 days |
| Patch released (critical) | 14 days |
| Patch released (moderate) | 30 days |

## Scope

**In scope:**
- IBOTVision SDK (this repository)
- SDK authentication and API key handling
- Broker connection logic
- NATS message handling in the connector layer

**Out of scope:**
- IBOTVision Core Runtime binary (closed-source — report via email, not GitHub)
- IBOTVision signal infrastructure servers
- Third-party broker software (IBKR, etc.)
- Social engineering or physical attacks

## Disclosure Policy

We follow coordinated responsible disclosure. We ask that you:
1. Give us reasonable time to patch before public disclosure
2. Not access, modify, or delete data belonging to other users
3. Not perform denial-of-service testing against live infrastructure

We will credit researchers in the release notes unless they prefer to remain
anonymous.

## Contact

security@ibotvision.com

IBOT Limited · Registered in Bulgaria (EU)
