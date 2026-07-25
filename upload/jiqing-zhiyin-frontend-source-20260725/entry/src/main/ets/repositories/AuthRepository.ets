import { AuthResponse, LoginRequest, RegisterRequest } from '../models/AuthModels';
import { AUTH_FIXTURE } from '../mock/MockFixtures';
import { authStore } from '../core/auth/AuthStore';
import { Environment } from '../core/config/Environment';
import { apiClient } from '../core/http/ApiProvider';

export class AuthRepository {
  async login(request: LoginRequest): Promise<AuthResponse> {
    const response = Environment.MOCK_MODE ? AUTH_FIXTURE : await apiClient.post<AuthResponse>('/auth/login/', request);
    await authStore.save(response.token, response.user);
    return response;
  }

  async register(request: RegisterRequest): Promise<AuthResponse> {
    const response: AuthResponse = Environment.MOCK_MODE ? {
      token: AUTH_FIXTURE.token,
      user: {
        id: AUTH_FIXTURE.user.id,
        username: request.username,
        nickname: request.nickname
      }
    } : await apiClient.post<AuthResponse>('/auth/register/', request);
    await authStore.save(response.token, response.user);
    return response;
  }

  async logout(): Promise<void> {
    await authStore.clear();
  }
}
