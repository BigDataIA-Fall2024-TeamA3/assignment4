// coagents-research-canvas/ui/src/components/SavedSessions.tsx

import { Button } from "@/components/ui/button";
import { useResearchSessions } from "@/lib/session";
import { ResearchSession } from "@/lib/types"; // Corrected import

type SavedSessionsProps = {
  loadSession: (session: ResearchSession) => void;
};

export function SavedSessions({ loadSession }: SavedSessionsProps) {
  const sessions = useResearchSessions();

  if (sessions.length === 0) {
    return <div className="text-sm text-slate-400">No saved sessions.</div>;
  }

  return (
    <div className="mt-4">
      <h3 className="text-md font-semibold mb-2">Saved Sessions</h3>
      <ul className="space-y-2">
        {sessions.map((session, index) => (
          <li key={index} className="flex justify-between items-center">
            <span>
              {new Date(session.timestamp).toLocaleString()} - {session.research_question}
            </span>
            <Button onClick={() => loadSession(session)} size="sm">
              Load
            </Button>
          </li>
        ))}
      </ul>
    </div>
  );
}
