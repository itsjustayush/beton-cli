const { spawnSync } = require("node:child_process");
const packageJson = require("../package.json");

const npmCommand = process.platform === "win32" ? "npm.cmd" : "npm";
console.log(`Updating ${packageJson.name} through npm...`);
const result = spawnSync(npmCommand, ["install", "--global", `${packageJson.name}@latest`], { stdio: "inherit" });
if (result.error) {
  console.error(`Could not start npm: ${result.error.message}`);
  process.exitCode = 1;
} else if (result.status !== 0) {
  process.exitCode = result.status || 1;
} else {
  console.log("BETON is updated. Run `beton --version` to verify the installed release.");
}
