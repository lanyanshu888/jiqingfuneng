const { opportunities } = require("../../utils/data");
const { setTabBar } = require("../../utils/tabbar");

Page({
  data: {
    tabs: ["全部", "本地就业", "实习见习", "基层实践", "志愿服务", "创业项目"],
    current: "全部",
    opportunities
  },

  onShow() {
    setTabBar(this, 2);
  },

  selectTab(e) {
    const current = e.currentTarget.dataset.tab;
    const list = current === "全部" ? opportunities : opportunities.filter((item) => item.type === current);
    this.setData({ current, opportunities: list });
  },

  goDetail(e) {
    wx.navigateTo({ url: `/pages/opportunity-detail/opportunity-detail?id=${e.currentTarget.dataset.id}` });
  }
});
