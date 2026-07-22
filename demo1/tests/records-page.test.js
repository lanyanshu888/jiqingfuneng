const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const projectRoot = path.resolve(__dirname, "..");

test("records page is registered and linked from mine page", () => {
  const appConfig = JSON.parse(fs.readFileSync(path.join(projectRoot, "app.json"), "utf8"));
  const mineScript = fs.readFileSync(path.join(projectRoot, "pages/mine/mine.js"), "utf8");

  assert.ok(appConfig.pages.includes("pages/records/records"));
  assert.match(mineScript, /\/pages\/records\/records/);
});

test("records page renders all growth record categories", () => {
  const template = fs.readFileSync(path.join(projectRoot, "pages/records/records.wxml"), "utf8");

  for (const title of ["活动报名", "岗位申请", "已完成课程", "导师咨询"]) {
    assert.match(template, new RegExp(title));
  }
});
