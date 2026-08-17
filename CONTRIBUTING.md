# Contributing to BETON

BETON is a local machine-control utility. Contributions should preserve the command language’s predictability, local-first behavior, and platform-aware implementation boundaries.

Before opening a pull request:

```bash
python -m pip install -e ".[dev]"
pytest
python -m compileall -q src
```

New machine-control commands should include a typed command definition, a platform adapter or service boundary, a dry-run path where an external action is involved, tests that do not launch real applications, and documentation with examples.

Avoid adding network dependencies to the core. Avoid arbitrary shell-string execution. Destructive actions must include confirmation behavior and should be reviewed carefully for Windows, macOS, and Linux differences.
