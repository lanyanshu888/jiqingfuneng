const { generateAgentBindingCode, getAgentDashboard } = require("../../utils/api");

Page({
  data: {
    loggedIn: false,
    loading: false,
    generating: false,
    bindingCode: "",
    remainingSeconds: 0,
    remainingText: "",
    suggestions: [],
    plan: null,
    error: ""
  },

  onShow() {
    const loggedIn = Boolean(wx.getStorageSync("authToken"));
    this.setData({ loggedIn });
    if (loggedIn) {
      this.loadDashboard();
    }
  },

  onUnload() {
    this.stopCountdown();
  },

  loadDashboard() {
    this.setData({ loading: true, error: "" });
    return getAgentDashboard()
      .then((data) => {
        this.setData({
          suggestions: data.suggestions || [],
          plan: data.plan || null
        });
      })
      .catch((error) => {
        this.setData({ error: error.message || "今日建议暂时无法加载" });
      })
      .finally(() => this.setData({ loading: false }));
  },

  generateBindingCode() {
    if (!wx.getStorageSync("authToken")) {
      wx.navigateTo({ url: "/pages/login/login" });
      return Promise.resolve();
    }
    this.setData({ generating: true });
    return generateAgentBindingCode()
      .then((data) => {
        this.setData({
          bindingCode: data.code,
          remainingSeconds: data.expiresIn || 600
        });
        this.updateRemainingText();
        this.startCountdown();
      })
      .catch((error) => {
        wx.showToast({ title: error.message || "绑定码生成失败", icon: "none" });
      })
      .finally(() => this.setData({ generating: false }));
  },

  startCountdown() {
    this.stopCountdown();
    this.countdownTimer = setInterval(() => {
      const next = this.data.remainingSeconds - 1;
      if (next <= 0) {
        this.stopCountdown();
        this.setData({ bindingCode: "", remainingSeconds: 0, remainingText: "绑定码已过期" });
        return;
      }
      this.setData({ remainingSeconds: next });
      this.updateRemainingText();
    }, 1000);
  },

  stopCountdown() {
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer);
      this.countdownTimer = null;
    }
  },

  updateRemainingText() {
    const minutes = Math.floor(this.data.remainingSeconds / 60);
    const seconds = this.data.remainingSeconds % 60;
    this.setData({ remainingText: `${minutes}:${String(seconds).padStart(2, "0")} 后失效` });
  },

  copyBindingCode() {
    if (!this.data.bindingCode) return;
    wx.setClipboardData({ data: this.data.bindingCode });
  },

  goLogin() {
    wx.navigateTo({ url: "/pages/login/login" });
  },

  goProfile() {
    wx.navigateTo({ url: "/pages/profile/profile" });
  }
});
