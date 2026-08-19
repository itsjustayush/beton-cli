const os = require("node:os");
const path = require("node:path");

const PACKAGE_NAME = "beton-cli";
const REPOSITORY = "https://github.com/itsjustayush/beton-cli.git";
const CURRENT_REF = process.env.BETON_SOURCE_REF || "v0.5.0";

function dataHome() {
  if (process.env.BETON_NPM_HOME) return process.env.BETON_NPM_HOME;
  if (process.platform === "win32") return path.join(process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming"), "Beton", "npm-runtime");
  if (process.platform === "darwin") return path.join(os.homedir(), "Library", "Application Support", "Beton", "npm-runtime");
  return path.join(process.env.XDG_DATA_HOME || path.join(os.homedir(), ".local", "share"), "beton", "npm-runtime");
}

function runtimeRoot() {
  return path.join(dataHome(), CURRENT_REF);
}

function pythonExecutable() {
  return process.platform === "win32"
    ? path.join(runtimeRoot(), ".venv", "Scripts", "python.exe")
    : path.join(runtimeRoot(), ".venv", "bin", "python");
}

function betonExecutable() {
  return process.platform === "win32"
    ? path.join(runtimeRoot(), ".venv", "Scripts", "beton.exe")
    : path.join(runtimeRoot(), ".venv", "bin", "beton");
}

module.exports = { CURRENT_REF, PACKAGE_NAME, REPOSITORY, betonExecutable, dataHome, pythonExecutable, runtimeRoot };
