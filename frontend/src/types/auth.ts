export type UserRole = 'super_admin' | 'school_admin' | 'teacher';

export const UserRole = {
  SUPER_ADMIN: 'super_admin',
  SCHOOL_ADMIN: 'school_admin',
  TEACHER: 'teacher',
} as const;

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

export interface UserInfo {
  id: string;
  username: string;
  role: UserRole;
  school_id?: string;
  school_name?: string;
  real_name?: string;
}
