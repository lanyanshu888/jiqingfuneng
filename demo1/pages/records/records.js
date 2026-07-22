const { getGrowthRecords } = require("../../utils/api");

Page({
  data: {
    loading: true,
    error: "",
    activities: [],
    opportunities: [],
    courses: [],
    consultations: [],
    favorites: []
  },

  onShow() {
    if (!wx.getStorageSync("authToken")) {
      this.setData({ loading: false, error: "请先登录后查看成长记录" });
      return;
    }
    this.setData({ loading: true, error: "" });
    getGrowthRecords().then((records) => {
      this.setData({
        loading: false,
        activities: records.activities || [],
        opportunities: records.opportunities || [],
        courses: records.courses || [],
        consultations: records.consultations || [],
        favorites: records.favorites || []
      });
    }).catch((error) => {
      this.setData({ loading: false, error: error.message || "暂时无法获取成长记录" });
    });
  }
});
