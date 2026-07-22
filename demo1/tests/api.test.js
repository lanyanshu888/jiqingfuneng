const test = require("node:test");
const assert = require("node:assert/strict");

global.getApp = () => ({ globalData: { apiBaseUrl: "https://example.test/api", token: "" } });

let lastRequest;
global.wx = {
  getStorageSync(key) {
    return key === "authToken" ? "test-token" : "";
  },
  request(options) {
    lastRequest = options;
    options.success({ statusCode: 200, data: { ok: true } });
  },
};

const api = require("../utils/api");

test("activity enrollment calls the activity enrollment endpoint", async () => {
  await api.enrollActivity(12);

  assert.equal(lastRequest.url, "https://example.test/api/activities/12/enroll/");
  assert.equal(lastRequest.method, "POST");
});

test("course completion calls the completion endpoint", async () => {
  await api.completeCourse(6);

  assert.equal(lastRequest.url, "https://example.test/api/courses/6/complete/");
  assert.equal(lastRequest.method, "POST");
});

test("growth records call the current user endpoint", async () => {
  await api.getGrowthRecords();

  assert.equal(lastRequest.url, "https://example.test/api/me/growth/");
  assert.equal(lastRequest.method, "GET");
});
