export interface User {
  id: string;
  name: string;
  email: string;
  roles: string[];
  permissions: string[];
}
export interface LoginRequest { email: string; password: string }
export interface RegisterRequest { name: string; email: string; password: string }
export interface AuthOptions { selfRegistration: boolean }
export interface AuthResponse { user: User }
export interface Role { name: string; description: string | null; permissions: string[] }
export interface Pagination { total: number; limit: number; offset: number }