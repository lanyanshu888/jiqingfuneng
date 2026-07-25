import { AuthResponse, UserSummary } from '../models/AuthModels';
import { AssistantResult } from '../models/AssistantModels';
import { DashboardResponse, GrowthPlan, GrowthRecords } from '../models/PlanModels';
import { YouthProfile, ProfileResult } from '../models/ProfileModels';
import { GrowthResource } from '../models/ResourceModels';

export const MOCK_USER: UserSummary = {
  id: 7,
  username: 'demo',
  nickname: '冀青青年'
};

export const AUTH_FIXTURE: AuthResponse = {
  token: 'mock-token-for-local-development',
  user: MOCK_USER
};

export const PROFILE_FIXTURE: YouthProfile = {
  name: '冀青青年',
  region: '沧州',
  education: '本科',
  major: '电子商务',
  goal: '县域数字运营',
  skills: ['内容策划', '数据分析', '活动执行'],
  completeness: 85
};

export const PROFILE_RESULT_FIXTURE: ProfileResult = {
  title: '你的青年成长画像',
  summary: '你更接近就业准备型，适合从县域数字运营和公共服务数字化切入。',
  strengths: ['内容表达基础好', '目标方向清晰', '愿意参加实践项目'],
  suggestions: ['补齐数据看板能力', '完成一次真实活动运营复盘', '关注本地青年就业政策']
};

export const PLAN_FIXTURE: GrowthPlan = {
  goal: '县域数字运营',
  progress: 42,
  todayTask: {
    id: 12,
    title: '完成一份县域短视频账号分析',
    description: '选择一个本地公共服务账号，记录内容主题、更新频率和互动数据。',
    stage: '7days',
    deadlineText: '今天 20:00',
    completed: false
  },
  tasks: [
    {
      id: 12,
      title: '完成一份县域短视频账号分析',
      description: '建立内容观察表，形成 300 字复盘。',
      stage: '7days',
      deadlineText: '今天 20:00',
      completed: false
    },
    {
      id: 21,
      title: '报名青年数字技能公开课',
      description: '完成课程报名并记录学习计划。',
      stage: '1month',
      deadlineText: '本周五',
      completed: false
    },
    {
      id: 33,
      title: '完成一次活动运营实践',
      description: '参与一次真实活动，沉淀流程和数据。',
      stage: '3months',
      deadlineText: '三个月内',
      completed: false
    }
  ]
};

export const DASHBOARD_FIXTURE: DashboardResponse = {
  nickname: '冀青青年',
  currentGoal: '县域数字运营',
  profileCompleteness: 85,
  progress: 42,
  suggestion: '今天适合先完成账号分析，再收藏一个岗位机会。',
  plan: PLAN_FIXTURE
};

export const RECORDS_FIXTURE: GrowthRecords = {
  favorites: 3,
  applications: 1,
  enrollments: 2,
  completedCourses: 1,
  consultations: 1
};

export const RESOURCES_FIXTURE: GrowthResource[] = [
  {
    id: 1,
    resourceType: 'policy',
    title: '高校毕业生基层就业补贴政策',
    region: '河北',
    category: '就业政策',
    description: '面向符合条件的高校毕业生，提供基层就业补贴和服务支持。',
    tags: ['就业', '补贴', '高校毕业生'],
    reasons: ['与你的就业目标相关', '适合近期申请'],
    sourceUrl: 'https://example.gov/policy/1',
    favorited: false
  },
  {
    id: 2,
    resourceType: 'opportunity',
    title: '县域数字运营实习岗',
    region: '沧州',
    category: '实习',
    description: '参与本地品牌内容运营、活动推广和数据复盘。',
    deadline: '2026-08-15',
    tags: ['数字运营', '实习', '沧州'],
    reasons: ['匹配你的目标岗位', '能补齐真实项目经验'],
    favorited: true,
    actionState: '可申请'
  },
  {
    id: 3,
    resourceType: 'course',
    title: '公共服务数据分析入门',
    category: '课程',
    description: '学习基础表格分析、指标设计和看板表达。',
    tags: ['数据分析', '课程'],
    reasons: ['补齐数据能力', '适合一周内完成'],
    favorited: false,
    actionState: '未完成'
  },
  {
    id: 4,
    resourceType: 'activity',
    title: '青年就业服务开放日',
    region: '石家庄',
    category: '活动',
    description: '现场了解就业服务、创业政策和导师咨询。',
    startsAt: '2026-08-03 14:00',
    tags: ['活动', '就业服务'],
    reasons: ['适合建立本地资源连接'],
    favorited: false,
    actionState: '可报名'
  },
  {
    id: 5,
    resourceType: 'mentor',
    title: '县域电商运营导师咨询',
    category: '导师',
    description: '围绕简历、项目选择和职业路径提供一次咨询。',
    tags: ['导师', '电商运营'],
    reasons: ['与你的目标方向相近'],
    favorited: false,
    actionState: '可预约'
  }
];

export const PROFILE_ANALYSIS_FIXTURE: AssistantResult = {
  action: 'profile_analysis',
  title: '你的青年成长画像',
  message: '你当前更接近就业准备型，目标是县域数字运营。',
  cards: [
    {
      id: 'strengths',
      title: '当前优势',
      summary: '内容创作和活动执行基础较好。',
      reasons: ['专业背景匹配', '已选择数字运营方向'],
      actionLabel: '查看成长计划'
    }
  ]
};

export const CAREER_PLAN_FIXTURE: AssistantResult = {
  action: 'career_plan',
  title: '职业成长计划',
  message: '建议先完成 7 天能力补齐，再进入 1 个月项目实践。',
  cards: [
    {
      id: 'plan',
      title: '下一步',
      summary: '今天完成账号分析，周内报名公开课。',
      reasons: ['任务小', '反馈快', '能形成作品'],
      actionLabel: '打开规划'
    }
  ]
};

export const POLICY_SEARCH_FIXTURE: AssistantResult = {
  action: 'policy_search',
  title: '政策检索结果',
  message: '找到 1 条与你相关的高校毕业生就业政策。',
  cards: [
    {
      id: 'policy-1',
      title: '基层就业补贴政策',
      summary: '建议先确认毕业年限、就业单位和社保条件。',
      reasons: ['地区匹配', '就业阶段匹配'],
      actionLabel: '查看政策',
      resourceType: 'policy',
      resourceId: 1
    }
  ]
};

export const RESOURCE_MATCH_FIXTURE: AssistantResult = {
  action: 'resource_match',
  title: '资源匹配',
  message: '为你匹配到岗位、课程和导师资源。',
  cards: [
    {
      id: 'opportunity-2',
      title: '县域数字运营实习岗',
      summary: '适合作为你的第一段运营实践。',
      reasons: ['目标岗位匹配', '有实践产出'],
      actionLabel: '查看资源',
      resourceType: 'opportunity',
      resourceId: 2
    }
  ]
};

export const DAILY_SUGGESTION_FIXTURE: AssistantResult = {
  action: 'daily_suggestion',
  title: '今日建议',
  message: '先完成一项可交付的小任务，再收藏一个近期截止的机会。',
  cards: [
    {
      id: 'daily',
      title: '今天 30 分钟',
      summary: '完成账号分析表的前三列。',
      reasons: ['耗时可控', '能推动计划进度'],
      actionLabel: '去完成'
    }
  ]
};

