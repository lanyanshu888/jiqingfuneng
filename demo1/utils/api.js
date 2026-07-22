const app = getApp();

function request(options) {
  const token = wx.getStorageSync("authToken") || app.globalData.token;

  return new Promise((resolve, reject) => {
    wx.request({
      url: `${app.globalData.apiBaseUrl}${options.url}`,
      method: options.method || "GET",
      data: options.data || {},
      header: {
        "content-type": "application/json",
        ...(token ? { Authorization: `Token ${token}` } : {})
      },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
          return;
        }
        reject(res.data || { message: "请求失败" });
      },
      fail: reject
    });
  });
}

function login(username, password) {
  return request({
    url: "/auth/login/",
    method: "POST",
    data: { username, password }
  });
}

function register(username, password, nickname) {
  return request({
    url: "/auth/register/",
    method: "POST",
    data: { username, password, nickname }
  });
}

function getMe() {
  return request({ url: "/auth/me/" });
}

function saveRemoteProfile(profile) {
  return request({
    url: "/profiles/me/",
    method: "POST",
    data: profile
  });
}

module.exports = {
  request,
  login,
  register,
  getMe,
  saveRemoteProfile
};
