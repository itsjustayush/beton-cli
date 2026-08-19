const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const { CURRENT_REF, REPOSITORY, pythonExecutable, runtimeRoot } = require("../lib/paths");

function run(command, args, options = {}) {
  const result = spawnSync(command, args, { stdio: "inherit", ...options });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`${command} ${args.join(" ")} exited with code ${result.status}`);
}

function findPython() {
  const candidates = process.platform === "win32" ? ["py", "python"] : ["python3", "python"];
  for (const candidate of candidates) {
    const probe = spawnSync(candidate, ["--version"], { stdio: "ignore" });
    if (probe.status === 0) return candidate;
  }
  return null;
}

function downloadSource(root) {
  fs.mkdirSync(path.dirname(root), { recursive: true });
  const archive = path.join(path.dirname(root), `${CURRENT_REF}.tar.gz`);
  const archiveRef = CURRENT_REF.startsWith("v") ? `tags/${CURRENT_REF}` : `heads/${CURRENT_REF}`;
  const url = process.env.BETON_SOURCE_URL || `https://github.com/itsjustayush/beton-cli/archive/refs/${archiveRef}.tar.gz`;
  if (process.platform === "win32") {
    run("powershell.exe", ["-NoProfile", "-Command", `Invoke-WebRequest -Uri '${url}' -OutFile '${archive}'`]);
  } else {
    run("curl", ["-fsSL", url, "-o", archive]);
  }
  const unpack = path.join(path.dirname(root), `${CURRENT_REF}-source`);
  fs.rmSync(unpack, { recursive: true, force: true });
  fs.mkdirSync(unpack, { recursive: true });
  if (process.platform === "win32") {
    run("tar", ["-xzf", archive, "-C", unpack, "--strip-components=1"]);
  } else {
    run("tar", ["-xzf", archive, "-C", unpack, "--strip-components=1"]);
  }
  fs.rmSync(root, { recursive: true, force: true });
  fs.renameSync(unpack, root);
  fs.rmSync(archive, { force: true });
}

function install() {
  const python = findPython();
  if (!python) {
    throw new Error("Python 3.10+ is required. Install it from https://www.python.org/downloads/ and rerun npm install -g beton-cli.");
  }
  const root = runtimeRoot();
  if (!fs.existsSync(path.join(root, "pyproject.toml"))) downloadSource(root);
  const venvPython = pythonExecutable();
  if (!fs.existsSync(venvPython)) {
    run(python, process.platform === "win32" && python === "py" ? ["-3", "-m", "venv", ".venv"] : ["-m", "venv", ".venv"], { cwd: root });
  }
  run(venvPython, ["-m", "pip", "install", "--upgrade", "pip"], { cwd: root });
  run(venvPython, ["-m", "pip", "install", "."], { cwd: root });
  console.log(`BETON ${CURRENT_REF} is installed through npm.`);
  console.log("Run: beton doctor");
}

module.exports = { install };

if (require.main === module) {
  try {
    install();
  } catch (error) {
    console.error(`beton-cli installation failed: ${error.message}`);
    process.exitCode = 1;
  }
}
