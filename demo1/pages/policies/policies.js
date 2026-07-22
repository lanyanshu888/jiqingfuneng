const { policies } = require("../../utils/data");
const { setTabBar } = require("../../utils/tabbar");
const { getPolicies } = require("../../utils/api");

Page({
  data: {
    categories: ["全部", "就业补贴", "创业贷款", "技能培训", "基层服务"],
    current: "全部",
    policies
  },

  onShow() {
    setTabBar(this, 1);
    getPolicies().then((result) => {
      if (result.items && result.items.length) {
        this.setData({ policies: result.items });
      }
    }).catch(() => {});
  },

  selectCategory(e) {
    const current = e.currentTarget.dataset.category;
    const list = current === "全部" ? policies : policies.filter((item) => item.category === current);
    this.setData({ current, policies: list });
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/policy-detail/policy-detail?id=${id}` });
  }
});
