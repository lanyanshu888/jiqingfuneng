const { courses } = require("../../utils/data");

Page({
  data: {
    course: null,
    finished: false
  },

  onLoad(options) {
    const course = courses.find((item) => item.id === options.id) || courses[0];
    const finishedIds = wx.getStorageSync("finishedCourses") || [];
    this.setData({ course, finished: finishedIds.includes(course.id) });
  },

  finishCourse() {
    const finishedIds = wx.getStorageSync("finishedCourses") || [];
    if (!finishedIds.includes(this.data.course.id)) {
      finishedIds.push(this.data.course.id);
      wx.setStorageSync("finishedCourses", finishedIds);
      const progress = wx.getStorageSync("growthProgress") || {};
      wx.setStorageSync("growthProgress", {
        ...progress,
        courseFinished: (progress.courseFinished || 0) + 1
      });
    }
    this.setData({ finished: true });
    wx.showToast({ title: "学习已记录", icon: "success" });
  }
});
