const { stats, policies, opportunities, courses, activities } = require("../../utils/data");
const { setTabBar } = require("../../utils/tabbar");

Page({
  data: {
    stats,
    profile: null,
    progress: {
      profile: false,
      policyViews: 0,
      courseFinished: 0,
      activityJoined: 0
    },
    recommendPolicy: policies[0],
    recommendOpportunity: opportunities[0],
    recommendCourse: courses[0],
    recommendActivity: activities[0]
  },

  onShow() {
    setTabBar(this, 0);
    const profile = wx.getStorageSync("growthProfile") || null;
    const progress = wx.getStorageSync("growthProgress") || {
      profile: false,
      policyViews: 0,
      courseFinished: 0,
      activityJoined: 0
    };

    this.setData({ profile, progress });
  },

  goProfile() {
    wx.navigateTo({ url: "/pages/profile/profile" });
  },

  goPolicy() {
    wx.switchTab({ url: "/pages/policies/policies" });
  },

  goOpportunity() {
    wx.switchTab({ url: "/pages/opportunities/opportunities" });
  },

  goGrowth() {
    wx.switchTab({ url: "/pages/growth/growth" });
  },

  goPolicyDetail() {
    wx.navigateTo({ url: `/pages/policy-detail/policy-detail?id=${this.data.recommendPolicy.id}` });
  },

  goOpportunityDetail() {
    wx.navigateTo({ url: `/pages/opportunity-detail/opportunity-detail?id=${this.data.recommendOpportunity.id}` });
  },

  goActivityDetail() {
    wx.navigateTo({ url: `/pages/activity-detail/activity-detail?id=${this.data.recommendActivity.id}` });
  },

  goCourseDetail() {
    wx.navigateTo({ url: `/pages/course-detail/course-detail?id=${this.data.recommendCourse.id}` });
  }
});
