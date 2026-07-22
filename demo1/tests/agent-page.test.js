const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const projectRoot = path.resolve(__dirname, "..");

test("agent page is registered and linked from mine page", () => {
  const appConfig = JSON.parse(fs.readFileSync(path.join(projectRoot, "app.json"), "utf8"));
  const mineScript = fs.readFileSync(path.join(projectRoot, "pages/mine/mine.js"), "utf8");

  assert.ok(appConfig.pages.includes("pages/agent/agent"));
  assert.match(mineScript, /\/pages\/agent\/agent/);
});

test("agent API uses user token endpoints without a service key", () => {
  const apiScript = fs.readFileSync(path.join(projectRoot, "utils/api.js"), "utf8");

  assert.match(apiScript, /function generateAgentBindingCode/);
  assert.match(apiScript, /\/agent\/binding-code\//);
  assert.match(apiScript, /function getAgentDashboard/);
  assert.match(apiScript, /\/agent\/me\/dashboard\//);
  assert.doesNotMatch(apiScript, /X-Agent-Service-Key/);
});

test("agent page renders binding, plan and daily suggestion sections", () => {
  const template = fs.readFileSync(path.join(projectRoot, "pages/agent/agent.wxml"), "utf8");

  for (const title of ["连接小艺", "一次性绑定码", "今日建议", "我的成长计划"]) {
    assert.match(template, new RegExp(title));
  }
});
