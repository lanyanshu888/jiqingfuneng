const { activities } = require("../../utils/data");
const { enrollActivity, getActivity } = require("../../utils/api");

Page({
  data: {
    activity: null,
    joined: false
  },

  onLoad(options) {
    const activity = activities.find((item) => item.id === options.id) || activities[0];
    const joinedIds = wx.getStorageSync("joinedActivities") || [];
    this.setData({ activity, joined: joinedIds.includes(activity.id) });
    if (/^\d+$/.test(String(options.id))) {
      getActivity(options.id).then((remoteActivity) => {
        this.setData({ activity: remoteActivity });
      }).catch(() => {});
    }
  },

  joinActivity() {
    if (wx.getStorageSync("authToken") && /^\d+$/.test(String(this.data.activity.id))) {
      enrollActivity(this.data.activity.id).then(() => {
        this.setData({ joined: true });
        wx.showToast({ title: "报名成功", icon: "success" });
      }).catch((error) => {
        wx.showToast({ title: error.message || "报名失败，请稍后重试", icon: "none" });
      });
      return;
    }
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
