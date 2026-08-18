## Summary

Describe the change and the user problem it solves.

## Implementation

Explain the command, platform adapter, service boundary, or documentation surface that changed. Mention any compatibility considerations.

## Validation

- [ ] `pytest`
- [ ] `python -m compileall -q src`
- [ ] Manual command or UI verification completed where relevant.
- [ ] Documentation and examples updated.

## Safety and privacy

- [ ] No arbitrary shell-string execution was introduced.
- [ ] External or disruptive actions have an explicit dry-run or confirmation path where applicable.
- [ ] No secrets, credentials, private paths, or personal data are included.
- [ ] Platform-specific behavior was considered for Linux, macOS, and Windows where relevant.

## Checklist

- [ ] The change is scoped and reviewable.
- [ ] Tests cover the behavior that changed.
- [ ] The README or deployed documentation is synchronized.
- [ ] Release notes or changelog updates are included when user-facing behavior changes.
