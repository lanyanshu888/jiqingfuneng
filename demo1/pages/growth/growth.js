const { courses, activities, mentors } = require("../../utils/data");
const { setTabBar } = require("../../utils/tabbar");

Page({
  data: {
    courses,
    activities,
    mentors,
    profile: null
  },

  onShow() {
    setTabBar(this, 3);
    this.setData({ profile: wx.getStorageSync("growthProfile") || null });
  },

  goCourse(e) {
    wx.navigateTo({ url: `/pages/course-detail/course-detail?id=${e.currentTarget.dataset.id}` });
  },

  goActivity(e) {
    wx.navigateTo({ url: `/pages/activity-detail/activity-detail?id=${e.currentTarget.dataset.id}` });
  },

  goMentor() {
    wx.navigateTo({ url: "/pages/mentor/mentor" });
  }
});
