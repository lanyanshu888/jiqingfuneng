import { AssistantResult } from '../models/AssistantModels';
import { DashboardResponse } from '../models/PlanModels';
import { Environment } from '../core/config/Environment';
import { apiClient } from '../core/http/ApiProvider';
import {
  CAREER_PLAN_FIXTURE,
  DAILY_SUGGESTION_FIXTURE,
  POLICY_SEARCH_FIXTURE,
  PROFILE_ANALYSIS_FIXTURE,
  RESOURCE_MATCH_FIXTURE
} from '../mock/MockFixtures';

export class AssistantRepository {
  async analyzeProfile(): Promise<AssistantResult> {
    if (!Environment.MOCK_MODE) {
      return apiClient.get<AssistantResult>('/assistant/profile-analysis/');
    }
    return PROFILE_ANALYSIS_FIXTURE;
  }

  async generateCareerPlan(goal: string): Promise<AssistantResult> {
    if (!Environment.MOCK_MODE) {
      return apiClient.post<AssistantResult>('/assistant/career-plan/', { goal });
    }
    return {
      action: CAREER_PLAN_FIXTURE.action,
      title: CAREER_PLAN_FIXTURE.title,
      message: `${CAREER_PLAN_FIXTURE.message} 目标：${goal}`
      ,
      cards: CAREER_PLAN_FIXTURE.cards
    };
  }

  async searchPolicies(keyword: string, region: string): Promise<AssistantResult> {
    if (!Environment.MOCK_MODE) {
      return apiClient.get<AssistantResult>(`/assistant/policy-search/?keyword=${encodeURIComponent(keyword)}&region=${encodeURIComponent(region)}&limit=5`);
    }
    return {
      action: POLICY_SEARCH_FIXTURE.action,
      title: POLICY_SEARCH_FIXTURE.title,
      message: `围绕“${keyword}”和“${region}”找到相关政策。`
      ,
      cards: POLICY_SEARCH_FIXTURE.cards
    };
  }

  async matchResources(goal: string): Promise<AssistantResult> {
    if (!Environment.MOCK_MODE) {
      return apiClient.post<AssistantResult>('/assistant/resource-match/', {
        resourceTypes: ['opportunity', 'course', 'activity', 'mentor'],
        goal,
        limit: 3
      });
    }
    return {
      action: RESOURCE_MATCH_FIXTURE.action,
      title: RESOURCE_MATCH_FIXTURE.title,
      message: `已按“${goal}”匹配资源。`
      ,
      cards: RESOURCE_MATCH_FIXTURE.cards
    };
  }

  async getDailySuggestion(): Promise<AssistantResult> {
    if (!Environment.MOCK_MODE) {
      const dashboard = await apiClient.get<DashboardResponse>('/agent/me/dashboard/');
      return {
        action: 'daily_suggestion',
        title: '今日建议',
        message: dashboard.suggestion,
        cards: [
          {
            id: `task-${dashboard.plan.todayTask.id}`,
            title: dashboard.plan.todayTask.title,
            summary: dashboard.plan.todayTask.description,
            reasons: [dashboard.plan.todayTask.deadlineText, `当前进度 ${Math.round(dashboard.progress)}%`],
            actionLabel: '查看任务'
          }
        ]
      };
    }
    return DAILY_SUGGESTION_FIXTURE;
  }
}
