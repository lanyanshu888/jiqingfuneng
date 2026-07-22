const { policies } = require("../../utils/data");
const { getPolicy } = require("../../utils/api");

Page({
  data: {
    policy: null
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
  }
});
