import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthUser {
  email: string;
  sub?: string;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  setSession: (t: { accessToken: string; refreshToken?: string; user: AuthUser }) => void;
  clear: () => void;
}

export const useAuth = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      setSession: ({ accessToken, refreshToken, user }) =>
        set({ accessToken, refreshToken: refreshToken ?? null, user }),
      clear: () => set({ accessToken: null, refreshToken: null, user: null }),
    }),
    { name: 'hotelstaff.auth' },
  ),
);
