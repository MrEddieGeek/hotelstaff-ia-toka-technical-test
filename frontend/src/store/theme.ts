import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type ThemeMode = 'light' | 'dark' | 'system';

interface ThemeState {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
  toggle: () => void;
}

const applyMode = (mode: ThemeMode) => {
  if (typeof document === 'undefined') return;
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
  const isDark = mode === 'dark' || (mode === 'system' && prefersDark);
  document.documentElement.classList.toggle('dark', isDark);
};

export const useTheme = create<ThemeState>()(
  persist(
    (set, get) => ({
      mode: 'system',
      setMode: (mode) => {
        applyMode(mode);
        set({ mode });
      },
      toggle: () => {
        const current = get().mode;
        const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
        const effective =
          current === 'system' ? (prefersDark ? 'dark' : 'light') : current;
        const next: ThemeMode = effective === 'dark' ? 'light' : 'dark';
        applyMode(next);
        set({ mode: next });
      },
    }),
    {
      name: 'hotelstaff.theme',
      onRehydrateStorage: () => (state) => {
        if (state) applyMode(state.mode);
        else applyMode('system');
      },
    },
  ),
);

if (typeof window !== 'undefined') {
  window
    .matchMedia?.('(prefers-color-scheme: dark)')
    .addEventListener('change', () => {
      const mode = useTheme.getState().mode;
      if (mode === 'system') applyMode('system');
    });
}
