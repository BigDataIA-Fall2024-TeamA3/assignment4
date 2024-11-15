// coagents-research-canvas/ui/src/components/QASection.tsx

import React, { useState } from "react";
import { Resource } from "@/lib/types";

type QASectionProps = {
  document: Resource;
  askQuestion: (docId: string, question: string) => void;
  qaResponses: Record<string, string>;
};

export function QASection({ document, askQuestion, qaResponses }: QASectionProps) {
  const [question, setQuestion] = useState("");

  const handleAskQuestion = () => {
    askQuestion(document.id, question);
    setQuestion("");
  };

  return (
    <div>
      <h3>{document.title}</h3>
      <div>
        {/* Display previous questions and answers */}
        {Object.entries(qaResponses).map(([q, a], index) => (
          <div key={index}>
            <p><strong>Q:</strong> {q}</p>
            <p><strong>A:</strong> {a}</p>
          </div>
        ))}
      </div>
      <div>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question"
        />
        <button onClick={handleAskQuestion}>Ask</button>
      </div>
    </div>
  );
}
