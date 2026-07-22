const { policies } = require("../../utils/data");

Page({
  data: {
    policy: null
  },

  onLoad(options) {
    const policy = policies.find((item) => item.id === options.id) || policies[0];
    this.setData({ policy });
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
  }
});
