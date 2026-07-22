const { stats, policies, opportunities, activities } = require("../../utils/data");

Page({
  data: {
    stats,
    tab: "数据看板",
    tabs: ["数据看板", "内容发布", "审核管理"],
    policies,
    opportunities,
    activities,
    auditItems: [
      { title: "黄骅市某企业发布数字运营岗位", type: "岗位审核", status: "待审核" },
      { title: "承德县实践基地提交成长营活动", type: "活动审核", status: "待审核" },
      { title: "创业政策申请材料更新", type: "政策更新", status: "待复核" }
    ]
  },

  selectTab(e) {
    this.setData({ tab: e.currentTarget.dataset.tab });
  },

  publish(e) {
    const title = e.detail.value.title;
    const type = e.detail.value.type;
    if (!title || !type) {
      wx.showToast({ title: "请填写标题和类型", icon: "none" });
      return;
    }
    wx.showToast({ title: "已加入待审核", icon: "success" });
  },

  approve(e) {
    const index = e.currentTarget.dataset.index;
    const auditItems = this.data.auditItems;
    auditItems[index].status = "已通过";
    this.setData({ auditItems });
  }
});
