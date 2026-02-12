"use client";

import { create } from "zustand";

type UIState = {
  selectedTemplate: string;
  setSelectedTemplate: (templateId: string) => void;
};

export const useUIStore = create<UIState>((set) => ({
  selectedTemplate: "minimal",
  setSelectedTemplate: (templateId) => set({ selectedTemplate: templateId }),
}));
