Page({
  enterApp() {
    wx.switchTab({ url: "/pages/index/index" });
  },

  goProfile() {
    wx.navigateTo({ url: "/pages/profile/profile" });
  },

  goLogin() {
    wx.navigateTo({ url: "/pages/login/login" });
  }
});
