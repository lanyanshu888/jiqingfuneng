import { describe, it, expect } from '@ohos/hypium';
import { ApiError } from '../../../main/ets/core/http/ApiError';

export default function apiClientTest(): void {
  describe('ApiClient', () => {
    it('mapsUnauthorizedError', 0, () => {
      const error = new ApiError(401, '登录已失效，请重新登录');
      expect(error.statusCode).assertEqual(401);
      expect(error.userMessage).assertEqual('登录已失效，请重新登录');
      expect(error.isUnauthorized()).assertTrue();
    });
  });
}

