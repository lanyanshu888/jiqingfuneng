import { AuthResponse, LoginRequest, MeResponse, RegisterRequest, UserSummary } from '../models/AuthModels';
import { AUTH_FIXTURE } from '../mock/MockFixtures';
import { authStore } from '../core/auth/AuthStore';
import { Environment } from '../core/config/Environment';
import { apiClient } from '../core/http/ApiProvider';

export class AuthRepository {
  async login(request: LoginRequest): Promise<AuthResponse> {
    if (Environment.AUTH_MOCK_MODE) {
      const response = AUTH_FIXTURE;
      await authStore.save(response.token, response.user);
      return response;
    }
    const response = await apiClient.post<AuthResponse>('/auth/login/', request);
    await authStore.save(response.token, response.user);
    return response;
  }

  async register(request: RegisterRequest): Promise<AuthResponse> {
    if (Environment.AUTH_MOCK_MODE) {
      const response: AuthResponse = {
        token: AUTH_FIXTURE.token,
        user: { id: AUTH_FIXTURE.user.id, username: request.username, nickname: request.nickname }
      };
      await authStore.save(response.token, response.user);
      return response;
    }
    const response = await apiClient.post<AuthResponse>('/auth/register/', request);
    await authStore.save(response.token, response.user);
    return response;
  }

  async validateToken(): Promise<UserSummary | null> {
    if (Environment.AUTH_MOCK_MODE) {
      return authStore.getUser();
    }
    try {
      const token = await authStore.getToken();
      if (token.length === 0) {
        return null;
      }
      const data = await apiClient.get<MeResponse>('/auth/me/');
      const user = data.user;
      if (user && user.id) {
        return user;
      }
      return null;
    } catch (_error) {
      return null;
    }
  }

  async logout(): Promise<void> {
    await authStore.clear();
  }
}
