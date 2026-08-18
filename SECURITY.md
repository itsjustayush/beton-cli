# Security Policy

BETON can launch local applications and system commands, so security issues are treated seriously. The project is designed to run with the current user’s permissions and to keep core data local.

## Supported versions

The latest published release is listed in the [GitHub Releases page](https://github.com/itsjustayush/beton-cli/releases). Security fixes, when applicable, are prioritized for the latest release and the `main` branch. Users should reproduce reports against the latest release before filing them whenever possible.

## Design principles

Beton should never require permanent administrator or root privileges. Elevation, when unavoidable for a narrowly scoped action, must be explicit. Destructive operations should require confirmation, and `--dry-run` must never perform the action. User input should be passed as validated argument vectors rather than concatenated shell strings. Core functionality should not silently upload notes, configuration, clipboard contents, or command results.

## Reporting a vulnerability

Do not publish an exploitable vulnerability in a public issue, pull request, discussion, or release note. Use GitHub’s [private security advisory form](https://github.com/itsjustayush/beton-cli/security/advisories/new). If that channel is unavailable, email [info.cometlabs@gmail.com](mailto:info.cometlabs@gmail.com) with the subject `BETON security report`.

Please include the affected version or commit, operating system and Python version, a concise description of the impact, reproducible steps or a minimal proof of concept, and any relevant logs with secrets and personal data removed. Do not attach live credentials, private keys, tokens, or unredacted clipboard contents.

## Response process

Maintainers will acknowledge a report when possible, validate the impact, coordinate a fix, and publish a release note or advisory after a remediation is available. Reporters will be credited in the advisory when they request it and when doing so does not create a safety or privacy concern. Please allow time for responsible triage before public disclosure.

## Scope

Reports involving command execution, unsafe argument handling, unintended network transmission, privilege escalation, local-data exposure, malicious release artifacts, dependency vulnerabilities, or documentation that would cause unsafe machine actions are in scope. General feature requests and ordinary command bugs belong in the public issue tracker unless they expose a security impact.
