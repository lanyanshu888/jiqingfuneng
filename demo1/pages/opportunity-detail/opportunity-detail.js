const { opportunities } = require("../../utils/data");
const { enrollOpportunity } = require("../../utils/api");

Page({
  data: {
    opportunity: null,
    joined: false
  },

  onLoad(options) {
    const opportunity = opportunities.find((item) => item.id === options.id) || opportunities[0];
    const joinedIds = wx.getStorageSync("joinedOpportunities") || [];
    this.setData({ opportunity, joined: joinedIds.includes(opportunity.id) });
  },

  join() {
    if (wx.getStorageSync("authToken") && /^\d+$/.test(String(this.data.opportunity.id))) {
      enrollOpportunity(this.data.opportunity.id).then(() => {
        this.setData({ joined: true });
        wx.showToast({ title: "申请已提交", icon: "success" });
      }).catch((error) => {
        wx.showToast({ title: error.message || "申请失败，请稍后重试", icon: "none" });
      });
      return;
    }
    const joinedIds = wx.getStorageSync("joinedOpportunities") || [];
    if (!joinedIds.includes(this.data.opportunity.id)) {
      joinedIds.push(this.data.opportunity.id);
      wx.setStorageSync("joinedOpportunities", joinedIds);
    }
    this.setData({ joined: true });
    wx.showToast({ title: "报名已提交", icon: "success" });
  }
});
