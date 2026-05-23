import { auth as rawAuth } from './client';
import type { LoginRequest, LoginResponse } from '../types';

export async function loginWithTelegram(data: LoginRequest): Promise<LoginResponse> {
  const jwt = await rawAuth.telegramLogin(data);
  await rawAuth.setCookie(jwt.token);
  return jwt;
}
