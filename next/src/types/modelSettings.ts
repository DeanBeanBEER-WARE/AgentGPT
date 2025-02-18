import type { Language } from "../utils/languages";

export const GPT_35_TURBO = "gpt-3.5-turbo" as const;
export const GPT_4 = "gpt-4" as const;
export const GPT_4O = "gpt-4o" as const;

export const GPT_MODEL_NAMES = [GPT_35_TURBO, GPT_4, GPT_4O] as const;
export type GPTModelNames = (typeof GPT_MODEL_NAMES)[number];

export const MAX_TOKENS = {
  [GPT_35_TURBO]: 4000,
  [GPT_4]: 8000,
  [GPT_4O]: 8000,
} as const;

export interface ModelSettings {
  language: Language;
  customApiKey: string;
  customModelName: GPTModelNames;
  customTemperature: number;
  customMaxLoops: number;
  maxTokens: number;
}

export const getModelMaxTokens = (model: GPTModelNames): number => {
  return MAX_TOKENS[model];
};
