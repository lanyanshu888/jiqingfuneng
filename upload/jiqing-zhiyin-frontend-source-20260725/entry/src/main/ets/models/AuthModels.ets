export interface UserSummary {
  id: number;
  username: string;
  nickname: string;
}

export interface MeResponse {
  user: UserSummary;
}

export interface AuthResponse {
  token: string;
  user: UserSummary;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest extends LoginRequest {
  nickname: string;
}

