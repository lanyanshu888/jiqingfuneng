import { describe, it, expect } from '@ohos/hypium';
import { AppState } from '../../../main/ets/state/AppState';

export default function appStateTest(): void {
  describe('AppState', () => {
    it('logsInAndLoadsDashboard', 0, async () => {
      const state = new AppState();
      const user = await state.login('demo', 'demo');
      expect(user.nickname).assertEqual('冀青青年');
      expect(state.dashboard() !== null).assertTrue();
    });
  });
}

