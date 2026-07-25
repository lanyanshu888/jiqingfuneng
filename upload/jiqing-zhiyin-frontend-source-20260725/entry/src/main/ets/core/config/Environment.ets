export class Environment {
  static readonly API_BASE_URL: string = 'https://api.jiqing.invalid/api';
  static readonly MOCK_MODE: boolean = true;
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

