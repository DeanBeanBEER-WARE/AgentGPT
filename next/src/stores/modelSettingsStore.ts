import type { StateCreator } from "zustand";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import { createSelectors } from "./helpers";
import type { ModelSettings, GPTModelNames } from "../types/modelSettings";
import { GPT_35_TURBO, getModelMaxTokens } from "../types/modelSettings";

const resetters: (() => void)[] = [];

interface ModelSettingsSlice {
  modelSettings: ModelSettings;
  updateSettings: <Key extends keyof ModelSettings>(key: Key, value: ModelSettings[Key]) => void;
}

const initialModelSettingsState = {
  modelSettings: {
    language: { name: "English", code: "en" },
    customApiKey: "",
    customModelName: GPT_35_TURBO,
    customTemperature: 0.9,
    customMaxLoops: 25,
    maxTokens: 4000,
  },
};

const createModelSettingsSlice: StateCreator<ModelSettingsSlice> = (set) => {
  resetters.push(() => set(initialModelSettingsState));

  return {
    ...initialModelSettingsState,
    updateSettings: <Key extends keyof ModelSettings>(key: Key, value: ModelSettings[Key]) => {
      set((state) => {
        const newSettings = { ...state.modelSettings, [key]: value };

        // Wenn das Modell geändert wird, passe die maxTokens an
        if (key === 'customModelName') {
          const modelName = value as GPTModelNames;
          const maxAllowedTokens = getModelMaxTokens(modelName);
          if (newSettings.maxTokens > maxAllowedTokens) {
            newSettings.maxTokens = maxAllowedTokens;
          }
        }

        return { modelSettings: newSettings };
      });
    },
  };
};

export const useModelSettingsStore = createSelectors(
  create<ModelSettingsSlice>()(
    persist(
      (...a) => ({
        ...createModelSettingsSlice(...a),
      }),
      {
        name: "agentgpt-settings-storage-v2",
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({
          modelSettings: state.modelSettings,
        }),
      }
    )
  )
);

export const resetSettings = () => resetters.forEach((resetter) => resetter());
