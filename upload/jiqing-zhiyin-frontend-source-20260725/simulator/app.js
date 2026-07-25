const initialState = {
  route: 'welcome',
  tab: 'home',
  online: true,
  user: null,
  profileReady: false,
  loginForm: { username: 'demo', passcode: 'demo' },
  registerForm: { nickname: '冀青青年', username: 'demo', passcode: 'demo' },
  profile: {
    region: '沧州',
    education: '本科',
    major: '电子商务',
    goal: '县域数字运营',
    completeness: 0
  },
  progress: 0,
  suggestion: '完成青年画像后，我会给你生成今日成长建议。',
  tasks: [
    { id: 12, stage: '7days', title: '完成一份县域短视频账号分析', detail: '记录内容主题、更新频率和互动数据。', deadline: '今天 20:00', done: false },
    { id: 21, stage: '1month', title: '报名青年数字技能公开课', detail: '完成课程报名并记录学习计划。', deadline: '本周五', done: false },
    { id: 33, stage: '3months', title: '完成一次活动运营实践', detail: '参与一次真实活动，沉淀流程和数据。', deadline: '三个月内', done: false }
  ],
  resourceType: 'policy',
  resources: [
    { id: 1, type: 'policy', title: '高校毕业生基层就业补贴政策', desc: '面向符合条件的高校毕业生，提供基层就业补贴和服务支持。', tags: ['就业', '补贴'], state: '可收藏', favorite: false },
    { id: 2, type: 'opportunity', title: '县域数字运营实习岗', desc: '参与本地品牌内容运营、活动推广和数据复盘。', tags: ['实习', '沧州'], state: '可申请', favorite: true },
    { id: 3, type: 'course', title: '公共服务数据分析入门', desc: '学习基础表格分析、指标设计和看板表达。', tags: ['课程', '数据'], state: '未完成', favorite: false },
    { id: 4, type: 'activity', title: '青年就业服务开放日', desc: '现场了解就业服务、创业政策和导师咨询。', tags: ['活动'], state: '可报名', favorite: false },
    { id: 5, type: 'mentor', title: '县域电商运营导师咨询', desc: '围绕简历、项目选择和职业路径提供一次咨询。', tags: ['导师'], state: '可预约', favorite: false }
  ],
  assistantMessage: '点击一个助手动作，我会返回结构化建议。',
  toast: ''
};

let state = clone(initialState);

const labels = {
  welcome: '启动',
  login: '登录',
  register: '注册',
  onboarding: '画像',
  home: '首页',
  plan: '规划',
  resource: '资源',
  assistant: '助手',
  mine: '我的',
  policy: '政策',
  opportunity: '岗位',
  course: '课程',
  activity: '活动',
  mentor: '导师'
};

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function html(strings, ...values) {
  return strings.map((part, index) => `${part}${values[index] ?? ''}`).join('');
}

function escapeAttr(value) {
  return String(value).replaceAll('"', '&quot;');
}

function routeTo(route) {
  state.route = route;
  state.toast = '';
  render();
}

function setTab(tab) {
  if (!state.user) {
    routeTo('login');
    return;
  }
  if (!state.profileReady) {
    routeTo('onboarding');
    return;
  }
  state.route = 'app';
  state.tab = tab;
  state.toast = '';
  render();
}

function setField(group, key, value) {
  state[group][key] = value;
}

function login() {
  state.user = {
    id: 7,
    username: state.loginForm.username || 'demo',
    nickname: '冀青青年'
  };
  state.toast = '登录成功，请继续完善青年画像。';
  routeTo('onboarding');
}

function register() {
  state.user = {
    id: 7,
    username: state.registerForm.username || 'demo',
    nickname: state.registerForm.nickname || '冀青青年'
  };
  state.toast = '注册成功，请继续完善青年画像。';
  routeTo('onboarding');
}

function completeProfile() {
  state.profileReady = true;
  state.profile.completeness = 85;
  state.progress = 42;
  state.suggestion = '今天适合先完成账号分析，再收藏一个岗位机会。';
  state.route = 'app';
  state.tab = 'home';
  state.toast = '画像已生成，成长计划已准备好。';
  render();
}

function logout() {
  state.user = null;
  state.profileReady = false;
  state.progress = 0;
  state.suggestion = '完成青年画像后，我会给你生成今日成长建议。';
  state.assistantMessage = '已退出登录，本地私有状态已清理。';
  state.route = 'welcome';
  render();
}

function updateMeta() {
  document.getElementById('statusText').textContent = state.online ? 'Mock 在线' : 'Mock 离线';
  document.getElementById('modeText').textContent = state.online ? 'Mock 在线' : 'Mock 离线';
  document.getElementById('userText').textContent = state.user ? state.user.nickname : '未登录';
  document.getElementById('progressText').textContent = `${state.progress}%`;
  document.getElementById('pageText').textContent = state.route === 'app' ? labels[state.tab] : labels[state.route];
  document.getElementById('tabbar').classList.toggle('hidden', state.route !== 'app');
  document.querySelectorAll('.tab').forEach((button) => {
    button.classList.toggle('active', button.dataset.tab === state.tab);
  });
}

function toast() {
  return state.toast ? `<article class="card toast"><p>${state.toast}</p></article>` : '';
}

function card(title, body, extra = '') {
  return html`<article class="card"><h3>${title}</h3><p>${body}</p>${extra}</article>`;
}

function welcomeView() {
  return html`
    <section class="page center">
      <div class="brand-mark">冀</div>
      <h2 class="title">冀青智引</h2>
      <p class="subtitle">注册、生成青年画像、执行成长计划、查看资源和接收本地提醒。</p>
      <button class="primary wide" onclick="routeTo('login')">登录</button>
      <button class="secondary wide" onclick="routeTo('register')">注册新账号</button>
    </section>
  `;
}

function loginView() {
  return html`
    <section class="page">
      <h2 class="title">登录</h2>
      <p class="subtitle">使用测试账号进入本地 Mock 流程。</p>
      <input value="${escapeAttr(state.loginForm.username)}" placeholder="用户名" oninput="setField('loginForm','username',this.value)">
      <input value="${escapeAttr(state.loginForm.passcode)}" placeholder="密码" type="password" oninput="setField('loginForm','passcode',this.value)">
      <button class="primary wide" onclick="login()">登录</button>
      <button class="secondary wide" onclick="routeTo('register')">去注册</button>
    </section>
  `;
}

function registerView() {
  return html`
    <section class="page">
      <h2 class="title">注册</h2>
      <input value="${escapeAttr(state.registerForm.nickname)}" placeholder="昵称" oninput="setField('registerForm','nickname',this.value)">
      <input value="${escapeAttr(state.registerForm.username)}" placeholder="用户名" oninput="setField('registerForm','username',this.value)">
      <input value="${escapeAttr(state.registerForm.passcode)}" placeholder="密码" type="password" oninput="setField('registerForm','passcode',this.value)">
      <button class="primary wide" onclick="register()">注册并登录</button>
      <button class="secondary wide" onclick="routeTo('login')">已有账号</button>
    </section>
  `;
}

function onboardingView() {
  return html`
    <section class="page">
      ${toast()}
      <h2 class="title">完善青年画像</h2>
      <p class="subtitle">模拟四步画像：地区、学历、专业、目标。</p>
      <input value="${escapeAttr(state.profile.region)}" placeholder="所在地区" oninput="setField('profile','region',this.value)">
      <input value="${escapeAttr(state.profile.education)}" placeholder="学历" oninput="setField('profile','education',this.value)">
      <input value="${escapeAttr(state.profile.major)}" placeholder="专业" oninput="setField('profile','major',this.value)">
      <input value="${escapeAttr(state.profile.goal)}" placeholder="成长目标" oninput="setField('profile','goal',this.value)">
      <button class="primary wide" onclick="completeProfile()">生成画像和计划</button>
    </section>
  `;
}

function homeView() {
  const task = state.tasks[0];
  return html`
    <section class="page">
      ${toast()}
      ${!state.online ? '<article class="card offline"><p>当前离线，正在显示最近保存的内容 · 更新于 22:56</p></article>' : ''}
      <h2 class="title">你好，${state.user.nickname}</h2>
      <p class="subtitle">${state.suggestion}</p>
      <article class="card">
        <div class="row"><h3>${state.profile.goal}</h3><strong>${state.progress}%</strong></div>
        <div class="progress" style="--value:${state.progress}%"><span></span></div>
        <p>画像完整度 ${state.profile.completeness}%</p>
      </article>
      ${card(task.title, task.detail, `<div class="row"><span class="notice">${task.deadline}</span><button class="primary" onclick="completeTask(${task.id})">${task.done ? '已完成' : '完成'}</button></div>`)}
      ${formPreview()}
    </section>
  `;
}

function formPreview() {
  const task = state.tasks.find((item) => !item.done) || state.tasks[0];
  return html`
    <article class="form-card">
      <strong>桌面成长卡片</strong>
      <span>${state.user ? task.title : '登录冀青智引，查看今日成长任务'}</span>
      <div class="progress" style="--value:${state.progress}%"><span></span></div>
      <small>${state.user ? task.deadline : '打开应用继续成长'}</small>
    </article>
  `;
}

function planView() {
  return html`
    <section class="page">
      <h2 class="title">成长规划</h2>
      <p class="subtitle">按 7 天、1 个月和 3 个月拆解目标。</p>
      ${state.tasks.map((task) => card(task.title, task.detail, `<div class="row"><span class="notice">${stageText(task.stage)} · ${task.deadline}</span><button class="${task.done ? 'secondary' : 'primary'}" onclick="completeTask(${task.id})">${task.done ? '已完成' : '完成'}</button></div>`)).join('')}
    </section>
  `;
}

function resourceView() {
  const resources = state.resources.filter((item) => item.type === state.resourceType);
  return html`
    <section class="page">
      <h2 class="title">资源中心</h2>
      ${!state.online ? '<article class="card offline"><p>离线模式只允许阅读缓存内容，收藏和报名等写操作会被阻止。</p></article>' : ''}
      <div class="chips">
        ${['policy', 'opportunity', 'course', 'activity', 'mentor'].map((type) => `<button class="chip ${state.resourceType === type ? 'active' : ''}" onclick="setResourceType('${type}')">${labels[type]}</button>`).join('')}
      </div>
      ${resources.map((item) => html`
        <article class="card resource">
          <div class="row"><h3>${item.title}</h3><span class="tag">${item.favorite ? '已收藏' : item.state}</span></div>
          <p>${item.desc}</p>
          <div class="chips">${item.tags.map((tag) => `<span class="tag">${tag}</span>`).join('')}</div>
          <div class="row">
            <button class="secondary" onclick="toggleFavorite(${item.id})">${item.favorite ? '取消收藏' : '收藏'}</button>
            <button class="primary" onclick="actResource(${item.id})">${actionLabel(item.type)}</button>
          </div>
        </article>
      `).join('')}
    </section>
  `;
}

function assistantView() {
  const actions = [
    ['画像分析', '你当前更接近就业准备型，适合从县域数字运营切入。'],
    ['生成职业计划', `已按“${state.profile.goal}”生成成长计划。`],
    ['政策搜索', `找到 ${state.profile.region} 高校毕业生就业相关政策。`],
    ['资源匹配', '匹配到岗位、课程和导师资源。'],
    ['今日建议', '先完成一项可交付的小任务。']
  ];
  return html`
    <section class="page">
      <h2 class="title">智能助手</h2>
      <p class="subtitle">${state.assistantMessage}</p>
      ${actions.map(([title, message]) => card(title, message, `<button class="primary" onclick="assistantAction('${message}')">执行</button>`)).join('')}
    </section>
  `;
}

function mineView() {
  return html`
    <section class="page">
      <h2 class="title">我的</h2>
      ${card(state.user.nickname, `当前目标：${state.profile.goal}`)}
      ${card('个人画像', `${state.profile.region} · ${state.profile.education} · ${state.profile.major}`)}
      ${card('成长记录', '收藏 3 · 申请 1 · 报名 2 · 完成课程 1 · 咨询 1')}
      ${card('提醒设置', '每日任务、活动、机会截止和规划复盘提醒')}
      ${formPreview()}
      <button class="danger wide" onclick="logout()">退出登录</button>
    </section>
  `;
}

function stageText(stage) {
  if (stage === '7days') {
    return '7 天';
  }
  if (stage === '1month') {
    return '1 个月';
  }
  return '3 个月';
}

function actionLabel(type) {
  return { policy: '查看来源', opportunity: '申请', course: '完成', activity: '报名', mentor: '预约' }[type];
}

function completeTask(id) {
  state.tasks = state.tasks.map((task) => task.id === id ? { ...task, done: true } : task);
  state.progress = Math.min(100, state.progress + 8);
  state.toast = '任务已完成，成长进度已更新。';
  render();
}

function setResourceType(type) {
  state.resourceType = type;
  render();
}

function toggleFavorite(id) {
  if (!state.online) {
    state.assistantMessage = '当前离线，联网后才能完成收藏操作。';
    state.tab = 'assistant';
    render();
    return;
  }
  state.resources = state.resources.map((item) => item.id === id ? { ...item, favorite: !item.favorite } : item);
  render();
}

function actResource(id) {
  if (!state.online) {
    state.assistantMessage = '当前离线，联网后才能完成此操作。';
    state.tab = 'assistant';
    render();
    return;
  }
  state.resources = state.resources.map((item) => item.id === id ? { ...item, state: `已${actionLabel(item.type)}` } : item);
  state.toast = '操作成功，成长记录已刷新。';
  render();
}

function assistantAction(message) {
  state.assistantMessage = message;
  render();
}

function render() {
  const view = document.getElementById('view');
  const views = {
    welcome: welcomeView,
    login: loginView,
    register: registerView,
    onboarding: onboardingView
  };
  const appViews = {
    home: homeView,
    plan: planView,
    resource: resourceView,
    assistant: assistantView,
    mine: mineView
  };
  view.innerHTML = state.route === 'app' ? appViews[state.tab]() : views[state.route]();
  updateMeta();
}

document.querySelectorAll('.tab').forEach((button) => {
  button.addEventListener('click', () => setTab(button.dataset.tab));
});

document.getElementById('resetBtn').addEventListener('click', () => {
  state = clone(initialState);
  render();
});

document.getElementById('offlineBtn').addEventListener('click', () => {
  state.online = !state.online;
  render();
});

render();
