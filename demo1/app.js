App({
  globalData: {
    appName: "冀青赋能",
    region: "河北省 沧州市",
    servicePhone: "0317-1234567",
    apiBaseUrl: "http://127.0.0.1:8000/api",
    token: "",
    user: null
  },

  onLaunch() {
    this.globalData.token = wx.getStorageSync("authToken") || "";
    this.globalData.user = wx.getStorageSync("currentUser") || null;
    const profile = wx.getStorageSync("growthProfile");
    if (!profile) {
      wx.setStorageSync("growthProgress", {
        profile: false,
        policyViews: 0,
        courseFinished: 0,
        activityJoined: 0
      });
    }
  }
});
