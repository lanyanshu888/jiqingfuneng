const { activities } = require("../../utils/data");

Page({
  data: {
    activity: null,
    joined: false
  },

  onLoad(options) {
    const activity = activities.find((item) => item.id === options.id) || activities[0];
    const joinedIds = wx.getStorageSync("joinedActivities") || [];
    this.setData({ activity, joined: joinedIds.includes(activity.id) });
  },

  joinActivity() {
    const joinedIds = wx.getStorageSync("joinedActivities") || [];
    if (!joinedIds.includes(this.data.activity.id)) {
      joinedIds.push(this.data.activity.id);
      wx.setStorageSync("joinedActivities", joinedIds);
      const progress = wx.getStorageSync("growthProgress") || {};
      wx.setStorageSync("growthProgress", {
        ...progress,
        activityJoined: (progress.activityJoined || 0) + 1
      });
    }
    this.setData({ joined: true });
    wx.showToast({ title: "报名成功", icon: "success" });
  }
});
