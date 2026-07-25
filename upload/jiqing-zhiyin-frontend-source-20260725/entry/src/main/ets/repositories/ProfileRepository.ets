import { ProfileResult, YouthProfile } from '../models/ProfileModels';
import { PROFILE_FIXTURE, PROFILE_RESULT_FIXTURE } from '../mock/MockFixtures';
import { Environment } from '../core/config/Environment';
import { apiClient } from '../core/http/ApiProvider';

export class ProfileRepository {
  private profile: YouthProfile = PROFILE_FIXTURE;

  async getMe(): Promise<YouthProfile> {
    if (!Environment.MOCK_MODE) {
      return apiClient.get<YouthProfile>('/profiles/me/');
    }
    return this.profile;
  }

  async save(profile: YouthProfile): Promise<ProfileResult> {
    if (!Environment.MOCK_MODE) {
      return apiClient.post<ProfileResult>('/profiles/me/', profile);
    }
    this.profile = profile;
    return PROFILE_RESULT_FIXTURE;
  }
}
