const api = require("../../utils/api");

Page({
  data: {
    mode: "login",
    loading: false
  },

  switchMode() {
    this.setData({ mode: this.data.mode === "login" ? "register" : "login" });
  },

  submit(e) {
    const values = e.detail.value;
    const username = (values.username || "").trim();
    const password = values.password || "";
    const nickname = (values.nickname || "").trim();

    if (!username || !password) {
      wx.showToast({ title: "请填写账号和密码", icon: "none" });
      return;
    }

    this.setData({ loading: true });
    const action = this.data.mode === "login"
      ? api.login(username, password)
      : api.register(username, password, nickname || username);

    action.then((res) => {
      getApp().globalData.token = res.token;
      getApp().globalData.user = res.user;
      wx.setStorageSync("authToken", res.token);
      wx.setStorageSync("currentUser", res.user);
      wx.showToast({ title: this.data.mode === "login" ? "登录成功" : "注册成功", icon: "success" });
      setTimeout(() => {
        wx.switchTab({ url: "/pages/mine/mine" });
      }, 500);
    }).catch((err) => {
      wx.showToast({ title: err.message || "后端未启动或账号信息有误", icon: "none" });
    }).finally(() => {
      this.setData({ loading: false });
    });
  }
});
