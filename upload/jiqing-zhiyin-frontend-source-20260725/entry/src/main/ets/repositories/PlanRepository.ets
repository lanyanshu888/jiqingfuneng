import { DashboardResponse, GrowthPlan, GrowthTask } from '../models/PlanModels';
import { DASHBOARD_FIXTURE, PLAN_FIXTURE } from '../mock/MockFixtures';
import { Environment } from '../core/config/Environment';
import { apiClient } from '../core/http/ApiProvider';

export class PlanRepository {
  private plan: GrowthPlan = PLAN_FIXTURE;

  async dashboard(): Promise<DashboardResponse> {
    if (!Environment.MOCK_MODE) {
      return apiClient.get<DashboardResponse>('/agent/me/dashboard/');
    }
    return {
      nickname: DASHBOARD_FIXTURE.nickname,
      currentGoal: DASHBOARD_FIXTURE.currentGoal,
      profileCompleteness: DASHBOARD_FIXTURE.profileCompleteness,
      suggestion: DASHBOARD_FIXTURE.suggestion,
      progress: this.plan.progress,
      plan: this.plan
    };
  }

  async getPlan(): Promise<GrowthPlan> {
    if (!Environment.MOCK_MODE) {
      const dashboard = await this.dashboard();
      return dashboard.plan;
    }
    return this.plan;
  }

  async completeTask(id: number): Promise<GrowthTask> {
    const nextTasks: GrowthTask[] = this.plan.tasks.map((task) => {
      if (task.id === id) {
        return {
          id: task.id,
          title: task.title,
          description: task.description,
          stage: task.stage,
          deadlineText: task.deadlineText,
          completed: true
        };
      }
      return task;
    });
    this.plan = {
      goal: this.plan.goal,
      progress: Math.min(100, this.plan.progress + 8),
      todayTask: this.plan.todayTask,
      tasks: nextTasks
    };
    const task = this.plan.tasks.find((item) => item.id === id);
    return task ? task : this.plan.todayTask;
  }
}
