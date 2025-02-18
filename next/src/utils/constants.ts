import { ENGLISH } from "./languages";
import type { ModelSettings } from "../types/modelSettings";

export const GPT_35_TURBO = "gpt-3.5-turbo" as const;
export const GPT_4 = "gpt-4" as const;
export const GPT_4O = "gpt-4o" as const;

export const GPT_MODEL_NAMES = [GPT_35_TURBO, GPT_4, GPT_4O] as const;
export type GPTModelNames = typeof GPT_MODEL_NAMES[number];

export const DEFAULT_MAX_LOOPS_FREE = 25 as const;
export const DEFAULT_MAX_LOOPS_CUSTOM_API_KEY = 10 as const;

export const MODEL_MAX_TOKENS = {
  [GPT_35_TURBO]: 4000,
  [GPT_4]: 8000,
  [GPT_4O]: 8000,
} as const;

export const getModelMaxTokens = (model: GPTModelNames): number => {
  return MODEL_MAX_TOKENS[model] || 4000;
};

export const getDefaultModelSettings = (): ModelSettings => {
  return {
    customApiKey: "",
    language: ENGLISH,
    customModelName: GPT_35_TURBO,
    customTemperature: 0.8,
    customMaxLoops: DEFAULT_MAX_LOOPS_FREE,
    maxTokens: 1250,
  };
};
