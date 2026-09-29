---
name: pre-release-technical-audit
description: Security and integrity checklist for Loopsense public release
iteration: 0
sources:
  - cowork
---

# Pre-Release Technical Audit

## Status
Dan approved 2026-09-23. Execution pending.

## Context
Making the entire Loopsense repository public requires a technical audit: dependencies with known vulnerabilities, exposed secrets, code quality baseline, and documentation standards. This checklist ensures the public tree is hardened before the GitHub extraction.

## Checklist

### A. Dependency Security Audit
- [ ] Run `npm audit` (or equivalent for Python/Go/Rust) on all package manifests
  - Document all known vulnerabilities found
  - Mark each as: unfixable / patchable / acceptable risk
  - For each: include mitigation strategy if present
- [ ] Check for outdated transitive dependencies
  - Flag any dependency > 2 years old without maintenance
  - Verify they have no known security issues
- [ ] Run SBOM generation (e.g., `syft`, `cyclonedx`) to document the software bill of materials for each agent/tool
- [ ] Record all findings in a `SECURITY.md` file in the repo root with:
  - Known vulnerabilities (version, CVE if available, impact)
  - Workarounds / mitigations in place
  - Deprecation timeline if any dependency will be removed

### B. Secrets & Credentials Scan
- [ ] Run `gitleaks` or equivalent on the full Git history
  - Flag any private keys, API keys, auth tokens, credentials
  - Flag any private URLs or internal endpoints
- [ ] Check `.env*` files and config templates for example values (not actual secrets)
- [ ] Scan commit messages for accidental credential references
- [ ] If any secrets are found:
  - Rotate all exposed credentials immediately
  - Add to `.gitignore` if not already there
  - Document the rotation in a private audit record
  - Record in `SECURITY.md` if the exposure was public-facing
- [ ] Add a pre-commit hook (`pre-commit` framework or similar) to prevent future secret commits

### C. Code Quality Baseline
- [ ] Establish a linting standard (if not already present)
  - ESLint for JS/TypeScript
  - pylint or black for Python
  - cargo clippy for Rust
  - Document in `CONTRIBUTING.md`
- [ ] Run linting on all agent SKILL.md, knowledge files, and code-bearing entities
  - No critical issues; document any accepted warnings
- [ ] Check documentation completeness:
  - README.md exists and describes the topology
  - `CONTRIBUTING.md` exists (linting, commit standards, entity scheme)
  - Each agent's SKILL.md is complete and current
  - Team registry (`knowledge/team-registry.md`) is up-to-date
- [ ] Verify no TODO/FIXME comments that describe unfixed bugs (optional FIXMEs for known limitations are OK if tracked)

### D. Public Content Audit (Re-verify Standing Rule 8)
- [ ] Re-run public-account review checklist:
  - All claims with evidence are source-linked
  - All characterizations of named people/accounts are fair and evidence-backed
  - No character attacks or unjustified disrespect
  - Tone is evidence-based throughout
- [ ] Ensure all claimed competencies, market positions, and success rates are either:
  - Directly linked to source data
  - Labeled as `hypothesis` or `working assumption`
  - Marked with certainty level (see [[claims-certainty-standard]])

### E. Documentation Standards
- [ ] Create or update `SECURITY.md` with:
  - Known vulnerabilities and mitigations
  - Credential rotation procedures
  - Responsible disclosure policy (if applicable)
  - How to report security issues
- [ ] Create or update `CONTRIBUTING.md` with:
  - Linting and code quality standards
  - Commit message format (including attribution lines)
  - Entity naming and file organization (reference standing rule 4)
  - Public-account review process (standing rule 8)
  - Claims and certainty labeling (reference [[claims-certainty-standard]])
- [ ] Create or update `CHANGELOG.md` (or `HISTORY.md`):
  - Document public release as initial commit (extraction start point)
  - Note that private audit trail remains in private repository
  - Record major iteration milestones

### F. Git History Sanitization (for public extraction)
- [ ] Confirm private audit trail (loopsense.log.json, history/ folder) is NOT in the public GitHub
- [ ] Verify extraction starts with a clean commit (no private Git objects)
- [ ] Document that the public tree is an extraction of the current working files, not a rebase of full history

## Completion Criteria

All sections A–F must be:
- ✓ Checked (specific finding or "none found")
- ✓ Documented (in SECURITY.md, CONTRIBUTING.md, or audit notes)
- ✓ Resolved (any issues either fixed, mitigated, or explicitly accepted with rationale)

No section may be marked "deferred to later iteration" without Dan's explicit written approval.

## Sign-Off

Audit completed: _____ (Loopy / Dan)
All items resolved: Yes / No
Ready for public extraction: Yes / No

