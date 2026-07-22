const { opportunities } = require("../../utils/data");

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
    const joinedIds = wx.getStorageSync("joinedOpportunities") || [];
    if (!joinedIds.includes(this.data.opportunity.id)) {
      joinedIds.push(this.data.opportunity.id);
      wx.setStorageSync("joinedOpportunities", joinedIds);
    }
    this.setData({ joined: true });
    wx.showToast({ title: "报名已提交", icon: "success" });
  }
});
