const { policies } = require("../../utils/data");
const { getPolicy, toggleFavorite } = require("../../utils/api");

Page({
  data: {
    policy: null,
    favorited: false
  },

  onLoad(options) {
    const policy = policies.find((item) => item.id === options.id) || policies[0];
    this.setData({ policy });
    if (/^\d+$/.test(String(options.id))) {
      getPolicy(options.id).then((remotePolicy) => {
        this.setData({ policy: remotePolicy });
      }).catch(() => {});
    }
    const progress = wx.getStorageSync("growthProgress") || {};
    wx.setStorageSync("growthProgress", {
      ...progress,
      policyViews: (progress.policyViews || 0) + 1
    });
  },

  callService() {
    wx.showModal({
      title: "咨询电话",
      content: this.data.policy.phone,
      showCancel: false
    });
  },

  toggleFavorite() {
    if (!wx.getStorageSync("authToken") || !/^\d+$/.test(String(this.data.policy.id))) {
      wx.showToast({ title: "请登录后收藏后台政策", icon: "none" });
      return;
    }
    toggleFavorite("policy", this.data.policy.id).then((result) => {
      this.setData({ favorited: result.favorited });
      wx.showToast({ title: result.favorited ? "已收藏" : "已取消收藏", icon: "success" });
    }).catch((error) => {
      wx.showToast({ title: error.message || "操作失败", icon: "none" });
    });
  }
});
