import { formBindingData, formProvider } from '@kit.FormKit';
import { DashboardResponse } from '../../models/PlanModels';

export interface GrowthFormData {
  loggedIn: boolean;
  taskTitle: string;
  progress: number;
  deadlineText: string;
  route: string;
}

class GrowthFormPayload {
  loggedIn: boolean = false;
  taskTitle: string = '';
  progress: number = 0;
  deadlineText: string = '';
  route: string = '';

  constructor(data: GrowthFormData) {
    this.loggedIn = data.loggedIn;
    this.taskTitle = data.taskTitle;
    this.progress = data.progress;
    this.deadlineText = data.deadlineText;
    this.route = data.route;
  }
}

export class GrowthFormService {
  private data: GrowthFormData = {
    loggedIn: false,
    taskTitle: '登录冀青智引，查看今日成长任务',
    progress: 0,
    deadlineText: '',
    route: 'login'
  };
  private activeFormIds: Set<string> = new Set();

  async registerForm(formId: string): Promise<void> {
    this.activeFormIds.add(formId);
    await this.updateForm(formId);
  }

  unregisterForm(formId: string): void {
    this.activeFormIds.delete(formId);
  }

  async updateFromDashboard(dashboard: DashboardResponse): Promise<void> {
    this.data = {
      loggedIn: true,
      taskTitle: dashboard.plan.todayTask.title,
      progress: dashboard.progress,
      deadlineText: dashboard.plan.todayTask.deadlineText,
      route: `task:${dashboard.plan.todayTask.id}`
    };
    await this.updateAllForms();
  }

  async showLoggedOut(): Promise<void> {
    this.data = {
      loggedIn: false,
      taskTitle: '登录冀青智引，查看今日成长任务',
      progress: 0,
      deadlineText: '',
      route: 'login'
    };
    await this.updateAllForms();
  }

  snapshotForTest(): GrowthFormData {
    return this.data;
  }

  private async updateAllForms(): Promise<void> {
    const formIds = Array.from(this.activeFormIds);
    for (let index = 0; index < formIds.length; index++) {
      await this.updateForm(formIds[index]);
    }
  }

  private async updateForm(formId: string): Promise<void> {
    try {
      const bindingData = formBindingData.createFormBindingData(new GrowthFormPayload(this.data));
      await formProvider.updateForm(formId, bindingData);
    } catch (error) {
    }
  }
}

export const growthFormService = new GrowthFormService();
