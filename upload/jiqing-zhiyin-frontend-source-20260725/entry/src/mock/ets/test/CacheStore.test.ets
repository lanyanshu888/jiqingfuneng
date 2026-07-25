import { describe, it, expect } from '@ohos/hypium';
import { CacheStore } from '../../../main/ets/core/cache/CacheStore';

export default function cacheStoreTest(): void {
  describe('CacheStore', () => {
    it('isolatesUserKeys', 0, async () => {
      const store = new CacheStore();
      expect(store.makeKey(7, 'dashboard.v1')).assertEqual('jiqing.cache.user.7.dashboard.v1');
      expect(store.makeKey(9, 'dashboard.v1')).assertEqual('jiqing.cache.user.9.dashboard.v1');
      await store.put(7, 'dashboard.v1', { value: 7 });
      await store.put(9, 'dashboard.v1', { value: 9 });
      await store.removeUser(7);
      const user9 = await store.get<object>(9, 'dashboard.v1');
      expect(user9 !== null).assertTrue();
    });
  });
}

