import { authStore } from '../core/auth/AuthStore';
import { cacheStore } from '../core/cache/CacheStore';
import { growthFormService } from '../core/form/GrowthFormService';
import { networkState } from '../core/network/NetworkState';
import { reminderService } from '../core/notification/ReminderService';
import { UserSummary } from '../models/AuthModels';
import { DashboardResponse } from '../models/PlanModels';
import { AuthRepository } from '../repositories/AuthRepository';
import { PlanRepository } from '../repositories/PlanRepository';
import { DemoState } from './DemoState';

export class AppState {
  private authRepository: AuthRepository = new AuthRepository();
  private planRepository: PlanRepository = new PlanRepository();
  private currentUser: UserSummary | null = null;
  private dashboardData: DashboardResponse | null = null;

  async bootstrap(): Promise<boolean> {
    if (DemoState.isActive()) {
      return true;
    }
    const user = await this.authRepository.validateToken();
    if (user) {
      this.currentUser = user;
      await this.refreshDashboard();
      return true;
    }
    return false;
  }

  async login(username: string, password: string): Promise<UserSummary> {
    DemoState.exit();
    const response = await this.authRepository.login({ username, password });
    this.currentUser = response.user;
    await this.refreshDashboard();
    return response.user;
  }

  async refreshDashboard(): Promise<DashboardResponse> {
    const dashboard = await this.planRepository.dashboard();
    this.dashboardData = dashboard;
    const user = await authStore.getUser();
    if (user) {
      await cacheStore.put(user.id, 'dashboard.v1', dashboard);
    }
    await growthFormService.updateFromDashboard(dashboard);
    return dashboard;
  }

  async logout(): Promise<void> {
    DemoState.exit();
    const user = await authStore.getUser();
    await this.authRepository.logout();
    if (user) {
      await cacheStore.removeUser(user.id);
    }
    await growthFormService.showLoggedOut();
    await reminderService.cancelAllForCurrentUser();
    this.currentUser = null;
    this.dashboardData = null;
  }

  user(): UserSummary | null {
    return this.currentUser;
  }

  dashboard(): DashboardResponse | null {
    return this.dashboardData;
  }

  isOnline(): boolean {
    return networkState.isOnline();
  }
}

export const appState = new AppState();
