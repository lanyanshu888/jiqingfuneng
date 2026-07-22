const { saveRemoteProfile } = require("../../utils/api");

const regionOptions = ["沧州市 黄骅市", "石家庄市 正定县", "秦皇岛市 海港区", "承德市 围场县", "邯郸市 丛台区", "雄安新区"];
const educationOptions = ["高中/中职", "大专", "本科", "硕士及以上"];
const statusOptions = ["在校", "待就业", "已就业", "创业中", "返乡发展"];
const intentOptions = ["想找工作", "想找实习", "想考公考编", "想创业", "想参加社会实践", "想提升技能", "想了解政策"];
const abilityOptions = ["简历已准备好", "有实习经历", "了解就业政策", "掌握办公软件", "会短视频/直播", "有创业想法"];

Page({
  data: {
    regionOptions,
    educationOptions,
    statusOptions,
    intentOptions,
    abilityOptions,
    regionIndex: 0,
    educationIndex: 2,
    statusIndex: 1,
    profile: null
  },

  onLoad() {
    const profile = wx.getStorageSync("growthProfile") || null;
    if (profile) {
      this.setData({ profile });
    }
  },

  bindRegion(e) {
    this.setData({ regionIndex: Number(e.detail.value) });
  },

  bindEducation(e) {
    this.setData({ educationIndex: Number(e.detail.value) });
  },

  bindStatus(e) {
    this.setData({ statusIndex: Number(e.detail.value) });
  },

  submitProfile(e) {
    const values = e.detail.value;
    const intents = values.intents || [];
    const abilities = values.abilities || [];
    const status = statusOptions[this.data.statusIndex];
    const type = this.buildType(status, intents, abilities);
    const tags = this.buildTags(type, intents, abilities);
    const profile = {
      nickname: values.nickname || "张同学",
      age: values.age || "20",
      major: values.major || "未填写专业",
      region: regionOptions[this.data.regionIndex],
      education: educationOptions[this.data.educationIndex],
      status,
      intents,
      abilities,
      type,
      tags,
      summary: `${status}｜${intents.slice(0, 3).join("、") || "待明确发展方向"}`
    };

    wx.setStorageSync("growthProfile", profile);
    wx.setStorageSync("growthProgress", {
      ...(wx.getStorageSync("growthProgress") || {}),
      profile: true
    });

    this.setData({ profile });
    wx.showToast({ title: "画像已生成", icon: "success" });

    if (wx.getStorageSync("authToken")) {
      saveRemoteProfile(profile).catch(() => {
        wx.showToast({ title: "本地已保存，后端同步失败", icon: "none" });
      });
    }
  },

  buildType(status, intents, abilities) {
    if (status === "创业中" || status === "返乡发展" || intents.includes("想创业")) {
      return "返乡创业型";
    }
    if (intents.includes("想参加社会实践")) {
      return "基层实践型";
    }
    if (intents.includes("想了解政策") && !intents.includes("想找工作")) {
      return "政策咨询型";
    }
    if (intents.includes("想提升技能") || !abilities.includes("掌握办公软件")) {
      return "技能提升型";
    }
    return "就业准备型";
  },

  buildTags(type, intents, abilities) {
    const tags = [type];
    if (intents.includes("想找实习")) tags.push("实习优先");
    if (intents.includes("想找工作")) tags.push("岗位匹配");
    if (intents.includes("想了解政策")) tags.push("政策提醒");
    if (abilities.includes("会短视频/直播")) tags.push("助农电商");
    if (!abilities.includes("简历已准备好")) tags.push("简历待完善");
    return tags;
  }
});
