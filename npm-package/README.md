# Beton CLI

**BETON** is a local-first command-line utility for everyday computer actions: opening apps and URLs, searching the web, saving notes, managing timers, reading the clipboard, and controlling supported system actions.

## Install

After `beton-cli` is published to npm, install it globally with:

```bash
npm install -g beton-cli
```

Then verify the installation:

```bash
beton doctor
beton --version
```

The npm package is a cross-platform launcher. It downloads the matching official Beton source release from GitHub, creates an isolated Python virtual environment in the user data directory, and installs the Python backend there. **Python 3.10 or newer is required; Git is not required for the npm path.** Node.js 18 or newer and npm are also required.

## Windows PowerShell and Command Prompt

The npm workflow does not require `Activate.ps1`, an execution-policy change, or a VS Code terminal. Install from ordinary PowerShell or Command Prompt:

```powershell
npm install -g beton-cli
beton doctor
beton note "installed from npm"
```

If Windows reports that Python is missing, install Python 3.10+ from [python.org](https://www.python.org/downloads/windows/) and rerun the npm command. The Python launcher (`py`) is supported automatically.

## Updating

For an npm-installed Beton instance, use:

```bash
beton version --upgrade
```

The wrapper updates itself through npm and then refreshes the matching Python runtime. You can also update directly with:

```bash
npm install -g beton-cli@latest
```

A source-checkout installation continues to use Beton’s Git-based upgrade flow.

## Source installation

The npm channel is the recommended one-line installation method. Beton remains available from the source repository for contributors and users who prefer a Git checkout:

```bash
git clone --branch v0.5.0 --depth 1 https://github.com/itsjustayush/beton-cli.git
cd beton-cli
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

See the complete documentation at [beton-cli.vercel.app/documentation](https://beton-cli.vercel.app/documentation).

## License

MIT © Ayush Bhattacharya and BETON contributors.
