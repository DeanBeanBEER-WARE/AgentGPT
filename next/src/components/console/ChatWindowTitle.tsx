import React from "react";
import type { GPTModelNames } from "../../types/modelSettings";
import { GPT_35_TURBO, GPT_4, GPT_4O } from "../../types/modelSettings";

export const ChatWindowTitle = ({ model }: { model: GPTModelNames }) => {
  switch (model) {
    case GPT_4O:
      return (
        <React.Fragment>
          Agent<span className="text-amber-500">GPT-4o</span>
        </React.Fragment>
      );
    case GPT_4:
      return (
        <React.Fragment>
          Agent<span className="text-amber-500">GPT-4</span>
        </React.Fragment>
      );
    case GPT_35_TURBO:
      return (
        <React.Fragment>
          Agent<span className="text-neutral-400">GPT-3.5</span>
        </React.Fragment>
      );
    default:
      return (
        <React.Fragment>
          Agent<span className="text-neutral-400">{model}</span>
        </React.Fragment>
      );
  }
};
