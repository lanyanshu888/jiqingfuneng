import { describe, it, expect } from '@ohos/hypium';
import { ReminderService } from '../../../main/ets/core/notification/ReminderService';

export default function reminderServiceTest(): void {
  describe('ReminderService', () => {
    it('movesQuietHoursToMorning', 0, () => {
      const service = new ReminderService();
      const date = new Date('2026-08-01T23:00:00');
      const moved = new Date(service.moveOutOfQuietHours(date.getTime()));
      expect(moved.getHours()).assertEqual(8);
    });
  });
}

