# Security policy

BETON can launch local applications and system commands, so security issues should be treated seriously.

## Design principles

Beton should run with the current user’s permissions by default. It should request elevation only for a narrowly scoped action and should never run a permanently privileged background daemon. Destructive operations should require explicit confirmation. User input should be passed as validated argument vectors rather than concatenated shell strings.

## Reporting

Do not publish an exploitable vulnerability in a public issue before maintainers have had an opportunity to investigate it. Until a dedicated security contact is configured, open a private security report through the repository hosting provider and include the affected version, operating system, reproduction steps, and impact.
