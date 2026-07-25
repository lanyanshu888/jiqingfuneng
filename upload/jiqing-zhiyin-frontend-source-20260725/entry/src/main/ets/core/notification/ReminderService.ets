import { notificationManager } from '@kit.NotificationKit';
import { GrowthPlan } from '../../models/PlanModels';

export interface GrowthReminder {
  id: number;
  type: 'task' | 'activity' | 'opportunity' | 'review';
  title: string;
  message: string;
  triggerAt: number;
  route: string;
}

export class ReminderService {
  private reminders: Map<number, GrowthReminder> = new Map();
  private slotReady: boolean = false;

  async requestPermission(): Promise<boolean> {
    try {
      await this.ensureSlot();
      return true;
    } catch (error) {
      return false;
    }
  }

  async schedule(reminder: GrowthReminder): Promise<void> {
    const safeReminder: GrowthReminder = {
      id: reminder.id,
      type: reminder.type,
      title: reminder.title,
      message: reminder.message,
      triggerAt: this.moveOutOfQuietHours(reminder.triggerAt),
      route: reminder.route
    };
    this.reminders.set(reminder.id, safeReminder);
    await this.publish(safeReminder);
  }

  async cancel(id: number): Promise<void> {
    this.reminders.delete(id);
    try {
      await notificationManager.cancel(id);
    } catch (error) {
    }
  }

  async cancelAllForCurrentUser(): Promise<void> {
    this.reminders.clear();
    try {
      await notificationManager.cancelAll();
    } catch (error) {
    }
  }

  async rescheduleFromPlan(plan: GrowthPlan): Promise<void> {
    await this.schedule({
      id: plan.todayTask.id,
      type: 'task',
      title: plan.todayTask.title,
      message: '今天的成长任务还没有完成',
      triggerAt: Date.now() + 3600000,
      route: `task:${plan.todayTask.id}`
    });
  }

  moveOutOfQuietHours(triggerAt: number): number {
    const date = new Date(triggerAt);
    const hour = date.getHours();
    if (hour >= 22 || hour < 8) {
      const moved = new Date(triggerAt);
      if (hour >= 22) {
        moved.setDate(moved.getDate() + 1);
      }
      moved.setHours(8, 0, 0, 0);
      return moved.getTime();
    }
    return triggerAt;
  }

  private async ensureSlot(): Promise<void> {
    if (this.slotReady) {
      return;
    }
    try {
      await notificationManager.addSlot(notificationManager.SlotType.SERVICE_INFORMATION);
      this.slotReady = true;
    } catch (error) {
      this.slotReady = false;
    }
  }

  private async publish(reminder: GrowthReminder): Promise<void> {
    try {
      await this.ensureSlot();
      const request: notificationManager.NotificationRequest = {
        id: reminder.id,
        appMessageId: `jiqing-reminder-${reminder.id}`,
        notificationSlotType: notificationManager.SlotType.SERVICE_INFORMATION,
        content: {
          notificationContentType: notificationManager.ContentType.NOTIFICATION_CONTENT_BASIC_TEXT,
          normal: {
            title: reminder.title,
            text: reminder.message,
            additionalText: reminder.route
          }
        }
      };
      await notificationManager.publish(request);
    } catch (error) {
    }
  }
}

export const reminderService = new ReminderService();
