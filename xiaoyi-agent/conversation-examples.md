# 对话示例

## 1. 首次绑定

- 用户：帮我看看适合我的岗位。
- Agent：可以。为了读取你的成长画像，请先在“冀青赋能”小程序进入“连接小艺 Agent”，生成六位绑定码。
- 用户：482731。
- Agent：调用 `bindAccount`。成功后说明已连接，不复述或保存该绑定码。

## 2. 补全画像

- Agent：调用 `profileContext` 后发现缺少地区和专业，只追问这两项。
- 用户：河北沧州黄骅，电子商务专业。
- Agent：先展示变更内容；用户确认后才调用更新操作。

## 3. 职业规划

- 用户：我想在县域做数字运营，帮我规划三个月。
- Agent：调用 `careerPlan`，按 7 天、1 个月、3 个月展示任务与截止时间。

## 4. 政策咨询

- 用户：沧州有没有适合高校毕业生的就业补贴？
- Agent：调用 `policySearch`，说明可能适用理由、仍需确认条件、材料、流程、发布机构和有效期。

## 5. 资源推荐

- 用户：给我推荐一门提升数字运营能力的课程。
- Agent：调用 `resourceMatch`，展示课程及评分理由，并询问是否加入行动计划。

## 6. 报名确认

- 用户：帮我报名这个成长营。
- Agent：首次调用 `growthAction`，复述活动名称并问“确认报名吗？”
- 用户：确认报名。
- Agent：携带确认令牌再次调用；仅在 `ok=true` 后说“报名成功”。

## 7. 今日建议

- 用户：我今天优先做什么？
- Agent：调用 `dailySuggestion`，先说逾期任务，再说 24 小时内到期任务，最后给一项匹配资源。

## English example

- User: What should I do today?
- Agent: Call `dailySuggestion`, answer briefly in English, then add: “中文关键步骤：先完成逾期任务，再查看今日匹配资源。”
