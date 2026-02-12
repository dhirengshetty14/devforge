"use client";

import { create } from "zustand";
import { AuthUser } from "@/types/api";
import { clearAuthTokens } from "@/lib/auth";

type AuthState = {
  user: AuthUser | null;
  setUser: (user: AuthUser | null) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => {
    clearAuthTokens();
    set({ user: null });
  },
}));
