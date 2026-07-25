export class Environment {
  static readonly API_BASE_URL: string = 'https://nest-pension-sprint-buys.trycloudflare.com/api';
  static readonly MOCK_MODE: boolean = true;
  static readonly AUTH_MOCK_MODE: boolean = false;
  static readonly PROFILE_MOCK_MODE: boolean = false;
  static readonly DEBUG: boolean = true;

  static assertReadyForRealApi(): void {
    if (!Environment.MOCK_MODE && Environment.API_BASE_URL.includes('.invalid')) {
      throw new Error('Real API build has not configured API_BASE_URL');
    }
    if (!Environment.DEBUG && Environment.MOCK_MODE) {
      throw new Error('Release build cannot enable MOCK_MODE');
    }
  }
}

