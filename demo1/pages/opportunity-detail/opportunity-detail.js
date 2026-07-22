const { opportunities } = require("../../utils/data");
const { enrollOpportunity, getOpportunity, toggleFavorite } = require("../../utils/api");

Page({
  data: {
    opportunity: null,
    joined: false,
    favorited: false
  },

  onLoad(options) {
    const opportunity = opportunities.find((item) => item.id === options.id) || opportunities[0];
    const joinedIds = wx.getStorageSync("joinedOpportunities") || [];
    this.setData({ opportunity, joined: joinedIds.includes(opportunity.id) });
    if (/^\d+$/.test(String(options.id))) {
      getOpportunity(options.id).then((remoteOpportunity) => {
        this.setData({ opportunity: remoteOpportunity });
      }).catch(() => {});
    }
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
  },

  toggleFavorite() {
    if (!wx.getStorageSync("authToken") || !/^\d+$/.test(String(this.data.opportunity.id))) {
      wx.showToast({ title: "请登录后收藏后台岗位", icon: "none" });
      return;
    }
    toggleFavorite("opportunity", this.data.opportunity.id).then((result) => {
      this.setData({ favorited: result.favorited });
      wx.showToast({ title: result.favorited ? "已收藏" : "已取消收藏", icon: "success" });
    }).catch((error) => {
      wx.showToast({ title: error.message || "操作失败", icon: "none" });
    });
  }
});
