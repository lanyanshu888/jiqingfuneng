const { courses, activities, mentors } = require("../../utils/data");
const { setTabBar } = require("../../utils/tabbar");
const { getActivities, getCourses } = require("../../utils/api");

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
    Promise.all([getCourses(), getActivities()]).then(([courseResult, activityResult]) => {
      this.setData({
        courses: courseResult.items && courseResult.items.length ? courseResult.items : this.data.courses,
        activities: activityResult.items && activityResult.items.length ? activityResult.items : this.data.activities
      });
    }).catch(() => {});
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
