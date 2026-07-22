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

test("opportunity enrollment calls the opportunity enrollment endpoint", async () => {
  await api.enrollOpportunity(9);

  assert.equal(lastRequest.url, "https://example.test/api/opportunities/9/enroll/");
  assert.equal(lastRequest.method, "POST");
});

test("resource list methods call their corresponding endpoints", async () => {
  await api.getPolicies();
  assert.equal(lastRequest.url, "https://example.test/api/policies/");

  await api.getOpportunities();
  assert.equal(lastRequest.url, "https://example.test/api/opportunities/");

  await api.getCourses();
  assert.equal(lastRequest.url, "https://example.test/api/courses/");

  await api.getActivities();
  assert.equal(lastRequest.url, "https://example.test/api/activities/");
});

test("policy detail calls the selected policy endpoint", async () => {
  await api.getPolicy(4);

  assert.equal(lastRequest.url, "https://example.test/api/policies/4/");
});

test("resource detail methods call their selected endpoints", async () => {
  await api.getOpportunity(2);
  assert.equal(lastRequest.url, "https://example.test/api/opportunities/2/");

  await api.getCourse(3);
  assert.equal(lastRequest.url, "https://example.test/api/courses/3/");

  await api.getActivity(5);
  assert.equal(lastRequest.url, "https://example.test/api/activities/5/");
});

test("recommendations call the authenticated recommendation endpoint", async () => {
  await api.getRecommendations();

  assert.equal(lastRequest.url, "https://example.test/api/recommendations/");
});

test("mentor methods load mentors and submit a consultation", async () => {
  await api.getMentors();
  assert.equal(lastRequest.url, "https://example.test/api/mentors/");

  await api.consultMentor(3, { question: "如何准备面试？" });
  assert.equal(lastRequest.url, "https://example.test/api/mentors/3/consult/");
  assert.equal(lastRequest.method, "POST");
  assert.deepEqual(lastRequest.data, { question: "如何准备面试？" });
});
