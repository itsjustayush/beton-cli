#!/usr/bin/env node

const fs = require("node:fs");
const { spawnSync } = require("node:child_process");
const path = require("node:path");
const { betonExecutable, runtimeRoot } = require("../lib/paths");

const args = process.argv.slice(2);
const scriptsDir = path.join(__dirname, "..", "scripts");
const installer = path.join(scriptsDir, "install.js");
const updater = path.join(scriptsDir, "update.js");

function run(command, commandArgs, options = {}) {
  const result = spawnSync(command, commandArgs, { stdio: "inherit", ...options });
  if (result.error) {
    console.error(`beton: ${result.error.message}`);
    process.exitCode = 1;
    return result.status || 1;
  }
  return result.status || 0;
}

function wantsUpgrade() {
  return args.includes("--upgrade") && args[0] === "version";
}

if (wantsUpgrade()) {
  process.exitCode = run(process.execPath, [updater]);
} else {
  const executable = betonExecutable();
  if (!fs.existsSync(executable)) {
    const installStatus = run(process.execPath, [installer]);
    if (installStatus !== 0) process.exit(installStatus);
  }
  process.exitCode = run(executable, args, {
    cwd: runtimeRoot(),
    env: { ...process.env, BETON_NPM_RUNTIME: "1" },
  });
}
