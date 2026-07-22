Component({
  data: {
    selected: 0,
    color: "#6B7280",
    selectedColor: "#2F80ED",
    list: [
      {
        pagePath: "/pages/index/index",
        text: "首页",
        icon: "首"
      },
      {
        pagePath: "/pages/policies/policies",
        text: "政策",
        icon: "策"
      },
      {
        pagePath: "/pages/opportunities/opportunities",
        text: "机会",
        icon: "岗"
      },
      {
        pagePath: "/pages/growth/growth",
        text: "成长",
        icon: "课"
      },
      {
        pagePath: "/pages/mine/mine",
        text: "我的",
        icon: "我"
      }
    ]
  },

  methods: {
    switchTab(e) {
      const index = e.currentTarget.dataset.index;
      const url = this.data.list[index].pagePath;
      wx.switchTab({ url });
    }
  }
});
