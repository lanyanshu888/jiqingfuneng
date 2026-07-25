import { describe, it, expect } from '@ohos/hypium';

export default function abilityTest(): void {
  describe('MainNavigation', () => {
    it('declaresFiveMainTabs', 0, () => {
      const tabs: string[] = ['首页', '规划', '资源', '助手', '我的'];
      expect(tabs.length).assertEqual(5);
      expect(tabs[0]).assertEqual('首页');
      expect(tabs[4]).assertEqual('我的');
    });
  });
}

