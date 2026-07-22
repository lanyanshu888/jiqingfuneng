const { mentors } = require("../../utils/data");

Page({
  data: {
    mentors: mentors.map((item) => ({
      ...item,
      initial: item.name.slice(0, 1)
    })),
    question: ""
  },

  reserve(e) {
    const mentor = this.data.mentors[e.currentTarget.dataset.index];
    wx.showModal({
      title: "预约已提交",
      content: `${mentor.name}｜${mentor.available}`,
      showCancel: false
    });
  },

  inputQuestion(e) {
    this.setData({ question: e.detail.value });
  },

  submitQuestion() {
    if (!this.data.question) {
      wx.showToast({ title: "请先填写问题", icon: "none" });
      return;
    }
    this.setData({ question: "" });
    wx.showToast({ title: "留言已提交", icon: "success" });
  }
});
