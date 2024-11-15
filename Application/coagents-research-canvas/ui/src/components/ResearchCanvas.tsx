// coagents-research-canvas/ui/src/components/ResearchCanvas.tsx

"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  useCoAgent,
  useCoAgentStateRender,
  useCopilotAction,
} from "@copilotkit/react-core";
import { Progress } from "./Progress";
import { EditResourceDialog } from "./EditResourceDialog";
import { AddResourceDialog } from "./AddResourceDialog";
import { Resources } from "./Resources";
import { useModelSelectorContext } from "@/lib/model-selector-provider";
import { DocumentSelectionDialog } from "./DocumentSelectionDialog";
import { ArxivSearchDialog } from "./ArxivSearchDialog";
import { WebSearchDialog } from "./WebSearchDialog";
import { QASection } from "./QASection";
import { NamespaceSelector } from "./NamespaceSelector";
import { SavedSessions } from "./SavedSessions";
import { Button } from "@/components/ui/button";
import { AgentState, Resource, ResearchSession } from "@/lib/types";

// Import actions
import { ArxivSearchAction, WebSearchAction, RAGAction } from "@/lib/actions";

export function ResearchCanvas() {
  const { model, agentName } = useModelSelectorContext();

  const { state, setState } = useCoAgent<AgentState>({
    name: agentName,
    initialState: {
      model,
      research_question: "",
      report: "",
      resources: [],
      logs: [],
      available_documents: [],
      selected_documents: [],
      retrieved_docs: [],
    },
  });

  // Initialize actions using useCopilotAction by passing the action object
  const invokeArxivSearch = useCopilotAction(ArxivSearchAction);
  const invokeWebSearch = useCopilotAction(WebSearchAction);
  const invokeRAG = useCopilotAction(RAGAction);

  useCoAgentStateRender({
    name: agentName,
    render: ({ state, nodeName, status }) => {
      if (!state.logs || state.logs.length === 0) {
        return null;
      }
      return <Progress logs={state.logs} />;
    },
  });

  const resources: Resource[] = state.resources || [];
  const setResources = (resources: Resource[]) => {
    setState({ ...state, resources });
  };

  const [newResource, setNewResource] = useState<Resource>({
    id: "",
    url: "",
    title: "",
    description: "",
    namespace: "",
  });
  const [isAddResourceOpen, setIsAddResourceOpen] = useState(false);

  const addResource = () => {
    if (
      newResource.id &&
      newResource.url &&
      newResource.title &&
      newResource.description &&
      newResource.namespace
    ) {
      setResources([...resources, { ...newResource }]);
      setNewResource({ id: "", url: "", title: "", description: "", namespace: "" });
      setIsAddResourceOpen(false);
    }
  };

  const removeResource = (id: string) => {
    setResources(resources.filter((resource: Resource) => resource.id !== id));
  };

  const [editResource, setEditResource] = useState<Resource | null>(null);
  const [originalUrl, setOriginalUrl] = useState<string | null>(null);
  const [isEditResourceOpen, setIsEditResourceOpen] = useState(false);

  const handleCardClick = (resource: Resource) => {
    setEditResource({ ...resource });
    setOriginalUrl(resource.id);
    setIsEditResourceOpen(true);
  };

  const updateResource = () => {
    if (editResource && originalUrl) {
      setResources(
        resources.map((resource) =>
          resource.id === originalUrl ? { ...editResource } : resource
        )
      );
      setEditResource(null);
      setOriginalUrl(null);
      setIsEditResourceOpen(false);
    }
  };

  // Document Selection
  const [selectedDocuments, setSelectedDocuments] = useState<Resource[]>([]);

  // Arxiv and Web Search Handlers
  const performArxivSearch = async (query: string) => {
    try {
      const response = await invokeArxivSearch({ query });
      // Handle response.results as needed
      console.log("Arxiv Search Results:", response.results);
    } catch (error) {
      console.error("Error performing Arxiv search:", error);
    }
  };

  const performWebSearch = async (query: string) => {
    try {
      const response = await invokeWebSearch({ queries: [query] });
      // Handle response.results as needed
      console.log("Web Search Results:", response.results);
    } catch (error) {
      console.error("Error performing Web search:", error);
    }
  };

  // Q&A Handlers
  const [qaResponses, setQaResponses] = useState<Record<string, Record<string, string>>>({});

  const askQuestion = (docId: string, question: string): void => {
    const doc = selectedDocuments.find((d) => d.id === docId);
    if (!doc) {
      console.error("Document not found for Q&A.");
      return;
    }
    const namespace = doc.namespace;

    (async () => {
      try {
        const response = await invokeRAG({ query: question, namespace });
        const answer = response.answer;
        setQaResponses((prev) => ({
          ...prev,
          [docId]: {
            ...(prev[docId] || {}),
            [question]: answer,
          },
        }));
      } catch (error) {
        console.error("Error asking question:", error);
      }
    })();
  };

  // Saving Research Sessions
  const saveSession = () => {
    const session: ResearchSession = {
      model,
      research_question: state.research_question,
      selected_documents: selectedDocuments,
      resources: resources,
      report: state.report,
      qa_responses: qaResponses,
      logs: state.logs || [],
      timestamp: new Date().toISOString(),
      available_documents: state.available_documents,
      retrieved_docs: state.retrieved_docs,
    };

    // Save to local storage
    const existingSessions = JSON.parse(localStorage.getItem("research_sessions") || "[]");
    existingSessions.push(session);
    localStorage.setItem("research_sessions", JSON.stringify(existingSessions));

    alert("Research session saved successfully!");
  };

  // Load Session Handler
  const loadSession = (session: ResearchSession) => {
    setState({
      model: session.model || state.model,
      research_question: session.research_question,
      resources: session.resources,
      report: session.report,
      logs: session.logs || [],
      available_documents: session.available_documents,
      selected_documents: session.selected_documents,
      retrieved_docs: session.retrieved_docs,
    });
    setSelectedDocuments(session.selected_documents);
    setQaResponses(session.qa_responses || {});
  };

  return (
    <div className="container w-full h-full p-10 bg-[#F5F8FF]">
      <div className="space-y-8">
        {/* Research Question */}
        <div>
          <h2 className="text-lg font-medium mb-3 text-primary">
            Research Question
          </h2>
          <Input
            placeholder="Enter your research question"
            value={state.research_question || ""}
            onChange={(e) =>
              setState({ ...state, research_question: e.target.value })
            }
            aria-label="Research question"
            className="bg-background px-6 py-8 border-0 shadow-none rounded-xl text-md font-extralight focus-visible:ring-0 placeholder:text-slate-400"
          />
        </div>

        {/* Resources */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-medium text-primary">Resources</h2>
            <div className="flex space-x-2">
              <EditResourceDialog
                isOpen={isEditResourceOpen}
                onOpenChange={setIsEditResourceOpen}
                editResource={editResource}
                setEditResource={setEditResource}
                updateResource={updateResource}
              />
              <AddResourceDialog
                isOpen={isAddResourceOpen}
                onOpenChange={setIsAddResourceOpen}
                newResource={newResource}
                setNewResource={setNewResource}
                addResource={addResource}
              />
            </div>
          </div>
          {resources.length === 0 && (
            <div className="text-sm text-slate-400">
              Click the button above to add resources.
            </div>
          )}

          {resources.length !== 0 && (
            <Resources
              resources={resources}
              handleCardClick={handleCardClick}
              removeResource={removeResource}
            />
          )}
        </div>

        {/* Namespace Selector and Search Actions */}
        <div>
          <div className="flex space-x-4 mb-4">
            <NamespaceSelector
              onSelectDocument={(doc) => {
                if (!selectedDocuments.find((d) => d.id === doc.id)) {
                  setSelectedDocuments([...selectedDocuments, doc]);
                }
              }}
            />
            <ArxivSearchDialog performArxivSearch={performArxivSearch} />
            <WebSearchDialog performWebSearch={performWebSearch} />
            <Button
              onClick={saveSession}
              className="bg-green-500 text-white"
            >
              Save Session
            </Button>
          </div>
        </div>

        {/* Selected Documents and Q&A */}
        <div>
          <h2 className="text-lg font-medium mb-3 text-primary">
            Selected Documents
          </h2>
          {selectedDocuments.length === 0 && (
            <div className="text-sm text-slate-400">
              No documents selected.
            </div>
          )}
          {selectedDocuments.length !== 0 && (
            <div className="space-y-4">
              {selectedDocuments.map((doc) => (
                <QASection
                  key={doc.id}
                  document={doc}
                  askQuestion={askQuestion}
                  qaResponses={qaResponses[doc.id] || {}}
                />
              ))}
            </div>
          )}
        </div>

        {/* Research Draft */}
        <div className="flex flex-col h-full">
          <h2 className="text-lg font-medium mb-3 text-primary">
            Research Draft
          </h2>
          <Textarea
            placeholder="Write your research draft here"
            value={state.report || ""}
            onChange={(e) => setState({ ...state, report: e.target.value })}
            rows={10}
            aria-label="Research draft"
            className="bg-background px-6 py-8 border-0 shadow-none rounded-xl text-md font-extralight focus-visible:ring-0 placeholder:text-slate-400"
            style={{ minHeight: "200px" }}
          />
        </div>

        {/* Saved Sessions */}
        <SavedSessions loadSession={loadSession} />
      </div>
    </div>
  );
}
