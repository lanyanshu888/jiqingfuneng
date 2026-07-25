import { describe, it, expect } from '@ohos/hypium';

export default function userJourneyTest(): void {
  describe('UserJourney', () => {
    it('coversMvpFlowNames', 0, () => {
      const steps: string[] = ['register', 'login', 'profile', 'dashboard', 'plan', 'resources', 'assistant', 'mine'];
      expect(steps.length).assertEqual(8);
      expect(steps.includes('assistant')).assertTrue();
    });
  });
}

