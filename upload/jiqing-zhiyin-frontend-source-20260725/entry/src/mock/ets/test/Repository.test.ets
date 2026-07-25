import { describe, it, expect } from '@ohos/hypium';
import { ResourceRepository } from '../../../main/ets/repositories/ResourceRepository';

export default function repositoryTest(): void {
  describe('Repository', () => {
    it('loadsPolicyResources', 0, async () => {
      const repository = new ResourceRepository();
      const items = await repository.list('policy');
      expect(items.length).assertLarger(0);
      expect(items[0].resourceType).assertEqual('policy');
    });
  });
}

