import { describe, it, expect } from '@ohos/hypium';
import { AuthStore } from '../../../main/ets/core/auth/AuthStore';

export default function authStoreTest(): void {
  describe('AuthStore', () => {
    it('storesAndClearsToken', 0, async () => {
      const store = new AuthStore();
      await store.save('token', { id: 1, username: 'demo', nickname: '青年' });
      expect(await store.getToken()).assertEqual('token');
      await store.clear();
      expect(await store.getToken()).assertEqual('');
    });
  });
}

