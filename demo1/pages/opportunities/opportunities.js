const { opportunities } = require("../../utils/data");
const { setTabBar } = require("../../utils/tabbar");
const { getOpportunities } = require("../../utils/api");

Page({
  data: {
    tabs: ["全部", "本地就业", "实习见习", "基层实践", "志愿服务", "创业项目"],
    current: "全部",
    opportunities
  },

  onShow() {
    setTabBar(this, 2);
    getOpportunities().then((result) => {
      if (result.items && result.items.length) {
        this.setData({ opportunities: result.items });
      }
    }).catch(() => {});
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
