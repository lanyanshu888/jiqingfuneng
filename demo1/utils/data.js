const stats = [
  { label: "已服务青年", value: "3,286" },
  { label: "已发布岗位", value: "428" },
  { label: "已开展活动", value: "36" },
  { label: "合作单位", value: "58" }
];

const policies = [
  {
    id: "p1",
    title: "高校毕业生就业见习补贴",
    region: "沧州市",
    category: "就业补贴",
    target: "毕业2年内未就业高校毕业生、16-24岁失业青年",
    support: "见习期间给予生活补贴，并提供岗位实践和就业服务。",
    conditions: ["已完成实名登记", "参加经认定的就业见习岗位", "见习期通常为3-12个月"],
    materials: ["身份证", "毕业证或学籍证明", "就业创业证", "见习协议"],
    process: ["线上提交申请", "平台初审材料", "见习单位确认", "人社部门复核发放"],
    location: "当地公共就业服务机构",
    phone: "0317-1234567",
    updatedAt: "2026-04-10",
    source: "河北省公共就业服务政策汇编"
  },
  {
    id: "p2",
    title: "青年创业担保贷款申请指南",
    region: "河北省",
    category: "创业贷款",
    target: "有创业项目或个体经营计划的高校毕业生、返乡青年",
    support: "符合条件可申请创业担保贷款，并按政策享受贴息支持。",
    conditions: ["有明确创业项目", "信用记录良好", "经营主体或创业计划清晰"],
    materials: ["身份证", "营业执照或创业计划书", "贷款申请表", "担保材料"],
    process: ["提交创业需求", "导师预评估", "对接经办银行", "完成审核放款"],
    location: "县区人社服务窗口 / 创业服务中心",
    phone: "0311-12333",
    updatedAt: "2026-03-28",
    source: "河北省创业担保贷款服务指南"
  },
  {
    id: "p3",
    title: "职业技能培训补贴",
    region: "邯郸市",
    category: "技能培训",
    target: "登记失业青年、职业院校学生、返乡就业青年",
    support: "参加认定培训并取得合格证明后，可按规定享受培训补贴。",
    conditions: ["选择备案培训机构", "完成规定课时", "通过结业或技能评价"],
    materials: ["身份证", "培训报名表", "结业证明", "银行卡信息"],
    process: ["选择课程", "报名培训", "完成考核", "申请补贴"],
    location: "县区就业训练中心",
    phone: "0310-12333",
    updatedAt: "2026-02-18",
    source: "地方人社部门公开政策"
  },
  {
    id: "p4",
    title: "大学生乡村振兴实践项目支持",
    region: "承德市",
    category: "基层服务",
    target: "愿意参与乡村调研、助农直播、基层治理的在校大学生",
    support: "提供实践岗位、交通补助、实践证明和导师指导。",
    conditions: ["所在学校或团组织推荐", "具备基本实践时间", "完成项目成果提交"],
    materials: ["学生证", "报名表", "安全承诺书"],
    process: ["选择实践项目", "提交报名", "项目组筛选", "签到参加并提交成果"],
    location: "县域青年中心 / 实践基地",
    phone: "0314-1234567",
    updatedAt: "2026-04-02",
    source: "县域青年实践项目库"
  }
];

const opportunities = [
  {
    id: "o1",
    title: "县域数字运营实习生",
    type: "实习见习",
    unit: "沧州某科技服务有限公司",
    location: "沧州开发区",
    pay: "100元/天",
    education: "本科及以上",
    major: "计算机、电子商务、新闻传播相关",
    duration: "2个月",
    applicants: 31,
    deadline: "2026-05-20",
    contact: "hr@jiqing.example",
    proof: true,
    online: true,
    tags: ["本地实习", "可开证明", "数字运营"],
    detail: "参与县域企业新媒体账号维护、活动页面更新和基础数据整理。"
  },
  {
    id: "o2",
    title: "乡村振兴短视频助农实践项目",
    type: "基层实践",
    unit: "承德某县青年实践基地",
    location: "承德市围场县",
    pay: "交通补贴+实践证明",
    education: "不限",
    major: "会拍摄、剪辑、直播优先",
    duration: "7天集中实践",
    applicants: 46,
    deadline: "2026-05-12",
    contact: "practice@jiqing.example",
    proof: true,
    online: true,
    tags: ["乡村振兴", "短视频", "团队实践"],
    detail: "围绕本地农产品进行内容策划、短视频拍摄和直播助农实践。"
  },
  {
    id: "o3",
    title: "青年志愿服务社区项目",
    type: "志愿服务",
    unit: "邯郸青年社区服务站",
    location: "邯郸市丛台区",
    pay: "志愿时长认证",
    education: "不限",
    major: "不限",
    duration: "每周六上午",
    applicants: 72,
    deadline: "2026-05-30",
    contact: "volunteer@jiqing.example",
    proof: true,
    online: true,
    tags: ["社区服务", "基层治理", "志愿时长"],
    detail: "参与社区青年服务、政策宣传、活动协助和居民需求收集。"
  },
  {
    id: "o4",
    title: "返乡青年创业项目合伙人招募",
    type: "创业项目",
    unit: "黄骅市青年创业园",
    location: "沧州黄骅市",
    pay: "创业导师+工位支持",
    education: "大专及以上",
    major: "电商、营销、农业相关优先",
    duration: "3个月孵化期",
    applicants: 18,
    deadline: "2026-06-05",
    contact: "startup@jiqing.example",
    proof: false,
    online: true,
    tags: ["创业孵化", "返乡发展", "导师辅导"],
    detail: "面向有农产品电商、社区服务、文旅内容项目想法的青年招募。"
  }
];

const courses = [
  {
    id: "c1",
    title: "简历制作入门课",
    category: "职业规划",
    target: "就业准备型青年",
    duration: "30分钟",
    teacher: "王老师",
    goal: "完成一份结构清楚、突出实践经历的基础简历。",
    materials: "简历模板、岗位关键词清单",
    certificate: true,
    progress: 35
  },
  {
    id: "c2",
    title: "县域青年面试表达训练",
    category: "面试技巧",
    target: "求职青年、职业院校学生",
    duration: "45分钟",
    teacher: "李经理",
    goal: "掌握自我介绍、项目经历表达和常见面试问题回答方法。",
    materials: "面试题库、表达练习表",
    certificate: true,
    progress: 0
  },
  {
    id: "c3",
    title: "返乡创业政策申请指南",
    category: "政策申请",
    target: "返乡创业型青年",
    duration: "20分钟",
    teacher: "赵老师",
    goal: "了解创业担保贷款、场地支持和创业培训申请路径。",
    materials: "申请流程图、材料清单",
    certificate: false,
    progress: 0
  },
  {
    id: "c4",
    title: "短视频电商助农基础课",
    category: "农村电商",
    target: "实践型青年、创业青年",
    duration: "50分钟",
    teacher: "周导师",
    goal: "完成一次农产品短视频脚本策划和直播卖点提炼。",
    materials: "脚本模板、直播话术卡",
    certificate: true,
    progress: 15
  }
];

const activities = [
  {
    id: "a1",
    title: "冀青赋能·县域大学生就业成长营",
    time: "2026年5月18日 09:00-17:00",
    place: "沧州交通学院 / 黄骅市青年中心",
    host: "项目团队、合作团委、学校就业部门",
    target: "在校大学生、待就业青年、返乡发展青年",
    capacity: 50,
    joined: 36,
    agenda: ["09:00 政策解读", "10:00 简历门诊", "14:00 企业岗位对接", "15:30 导师答疑"],
    tags: ["就业成长营", "线下活动", "导师答疑"]
  },
  {
    id: "a2",
    title: "短视频电商助农训练营",
    time: "2026年5月25日 14:00-18:00",
    place: "承德县域实践基地",
    host: "青年实践基地、县域企业",
    target: "会拍摄、剪辑、直播或想参与乡村振兴的青年",
    capacity: 40,
    joined: 22,
    agenda: ["14:00 产品卖点拆解", "15:00 短视频脚本训练", "16:30 直播模拟", "17:30 项目报名"],
    tags: ["助农", "短视频", "实践"]
  }
];

const mentors = [
  {
    id: "m1",
    name: "王老师",
    role: "职业规划导师",
    goodAt: "简历修改、就业选择、职业路径规划",
    available: "周三 19:00-20:00"
  },
  {
    id: "m2",
    name: "李经理",
    role: "企业HR导师",
    goodAt: "面试技巧、企业招聘、岗位能力分析",
    available: "周五 18:30-19:30"
  },
  {
    id: "m3",
    name: "赵老师",
    role: "创业导师",
    goodAt: "创业计划书、政策申请、项目孵化",
    available: "周日 10:00-11:30"
  }
];

module.exports = {
  stats,
  policies,
  opportunities,
  courses,
  activities,
  mentors
};
