export interface BackendProfile {
  nickname: string;
  age: number | null;
  region: string;
  education: string;
  major: string;
  status: string;
  type: string;
  intents: string[];
  abilities: string[];
  tags: string[];
  summary: string;
}

export interface YouthProfile {
  name: string;
  region: string;
  education: string;
  major: string;
  goal: string;
  skills: string[];
  completeness: number;
}

export interface ProfileResult {
  title: string;
  summary: string;
  strengths: string[];
  suggestions: string[];
}

export interface ProfileResponse {
  profile: BackendProfile;
}

export interface ProfileSaveRequest {
  region?: string;
  education?: string;
  major?: string;
  status?: string;
  intents?: string[];
  abilities?: string[];
  summary?: string;
}
