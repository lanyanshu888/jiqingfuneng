const { setTabBar } = require("../../utils/tabbar");
const { getGrowthRecords } = require("../../utils/api");

Page({
  data: {
    profile: null,
    progress: {
      profile: false,
      policyViews: 0,
      courseFinished: 0,
      activityJoined: 0
    },
    points: 0,
    avatarText: "青",
    tagCount: 0,
    user: null,
    loginText: "未登录",
    menus: [
      { title: "连接小艺 Agent", url: "/pages/agent/agent" },
      { title: "我的画像", url: "/pages/profile/profile" },
      { title: "我的成长记录", url: "/pages/records/records" },
      { title: "我的课程", type: "tab", url: "/pages/growth/growth" },
      { title: "我的岗位申请", type: "tab", url: "/pages/opportunities/opportunities" },
      { title: "我的导师咨询", url: "/pages/mentor/mentor" },
      { title: "后台管理演示", url: "/pages/admin/admin" }
    ]
  },

  onShow() {
    setTabBar(this, 4);
    const user = wx.getStorageSync("currentUser") || null;
    const profile = wx.getStorageSync("growthProfile") || null;
    const progress = wx.getStorageSync("growthProgress") || {
      profile: false,
      policyViews: 0,
      courseFinished: 0,
      activityJoined: 0
    };
    const points = (progress.profile ? 10 : 0) + progress.policyViews * 5 + progress.courseFinished * 20 + progress.activityJoined * 20;
    const display = {
      profile,
      progress,
      points,
      user,
      loginText: user ? `已登录：${user.username}` : "未登录",
      avatarText: profile ? profile.nickname.slice(0, 1) : "青",
      tagCount: profile ? profile.tags.length : 0
    };
    this.setData(display);

    if (user && wx.getStorageSync("authToken")) {
      getGrowthRecords().then((records) => {
        const remoteProgress = {
          ...progress,
          activityJoined: records.activities.length,
          courseFinished: records.courses.length
        };
        this.setData({
          progress: remoteProgress,
          points: (remoteProgress.profile ? 10 : 0) + remoteProgress.policyViews * 5 + remoteProgress.courseFinished * 20 + remoteProgress.activityJoined * 20
        });
      }).catch(() => {});
    }
  },

  goLogin() {
    wx.navigateTo({ url: "/pages/login/login" });
  },

  logout() {
    wx.removeStorageSync("authToken");
    wx.removeStorageSync("currentUser");
    getApp().globalData.token = "";
    getApp().globalData.user = null;
    this.setData({ user: null });
    wx.showToast({ title: "已退出登录", icon: "success" });
  },

  goProfile() {
    wx.navigateTo({ url: "/pages/profile/profile" });
  },

  handleMenu(e) {
    const item = this.data.menus[e.currentTarget.dataset.index];
    if (item.type === "toast") {
      wx.showToast({ title: item.text, icon: "none" });
      return;
    }
    if (item.type === "tab") {
      wx.switchTab({ url: item.url });
      return;
    }
    wx.navigateTo({ url: item.url });
  }
});
