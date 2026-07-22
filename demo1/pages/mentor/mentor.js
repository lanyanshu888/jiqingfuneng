const { mentors } = require("../../utils/data");
const { consultMentor, getMentors } = require("../../utils/api");

function normalizeMentor(item) {
  const name = item.name || item.title;
  return {
    ...item,
    name,
    goodAt: item.goodAt || item.good_at,
    initial: name.slice(0, 1)
  };
}

Page({
  data: {
    mentors: mentors.map(normalizeMentor),
    question: "",
    selectedMentorIndex: 0
  },

  onShow() {
    getMentors().then((result) => {
      if (result.items && result.items.length) {
        this.setData({ mentors: result.items.map(normalizeMentor) });
      }
    }).catch(() => {});
  },

  reserve(e) {
    const index = e.currentTarget.dataset.index;
    const mentor = this.data.mentors[index];
    this.setData({ selectedMentorIndex: index });
    if (wx.getStorageSync("authToken") && /^\d+$/.test(String(mentor.id))) {
      consultMentor(mentor.id, { question: "预约咨询", scheduledAt: mentor.available }).then(() => {
        wx.showToast({ title: "预约已提交", icon: "success" });
      }).catch((error) => {
        wx.showToast({ title: error.message || "预约失败", icon: "none" });
      });
      return;
    }
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
    const mentor = this.data.mentors[this.data.selectedMentorIndex] || this.data.mentors[0];
    if (wx.getStorageSync("authToken") && mentor && /^\d+$/.test(String(mentor.id))) {
      consultMentor(mentor.id, { question: this.data.question }).then(() => {
        this.setData({ question: "" });
        wx.showToast({ title: "留言已提交", icon: "success" });
      }).catch((error) => {
        wx.showToast({ title: error.message || "提交失败", icon: "none" });
      });
      return;
    }
    this.setData({ question: "" });
    wx.showToast({ title: "留言已保存为演示记录", icon: "none" });
  }
});
