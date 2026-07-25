import { BackendProfile, ProfileResponse, ProfileSaveRequest, YouthProfile } from '../models/ProfileModels';
import { PROFILE_FIXTURE } from '../mock/MockFixtures';
import { Environment } from '../core/config/Environment';
import { apiClient } from '../core/http/ApiProvider';

export class ProfileRepository {
  private cached: BackendProfile | null = null;

  async getMyProfile(): Promise<BackendProfile> {
    if (Environment.PROFILE_MOCK_MODE) {
      return this.mockToBackend(PROFILE_FIXTURE);
    }
    const data = await apiClient.get<ProfileResponse>('/profiles/me/');
    this.cached = data.profile;
    return data.profile;
  }

  async saveMyProfile(request: ProfileSaveRequest): Promise<BackendProfile> {
    if (Environment.PROFILE_MOCK_MODE) {
      // In mock mode, just update local cache
      const current = this.cached ? this.cached : this.mockToBackend(PROFILE_FIXTURE);
      const updated: BackendProfile = {
        nickname: current.nickname,
        age: current.age,
        region: request.region ?? current.region,
        education: request.education ?? current.education,
        major: request.major ?? current.major,
        status: request.status ?? current.status,
        type: current.type,
        intents: request.intents ?? current.intents,
        abilities: request.abilities ?? current.abilities,
        tags: current.tags,
        summary: request.summary ?? current.summary
      };
      this.cached = updated;
      return updated;
    }
    const data = await apiClient.post<ProfileResponse>('/profiles/me/', request);
    this.cached = data.profile;
    return data.profile;
  }

  private mockToBackend(mock: YouthProfile): BackendProfile {
    return {
      nickname: mock.name,
      age: null,
      region: mock.region,
      education: mock.education,
      major: mock.major,
      status: '',
      type: '',
      intents: [mock.goal],
      abilities: mock.skills,
      tags: [],
      summary: ''
    };
  }
}
