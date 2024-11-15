// coagents-research-canvas/ui/src/app/api/copilotkit/route.ts
import {
  CopilotRuntime,
  OpenAIAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import OpenAI from "openai";
import { NextRequest } from "next/server";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const llmAdapter = new OpenAIAdapter({ openai });

const runtime = new CopilotRuntime({
  remoteActions: [
    {
      url: "http://localhost:8000/copilotkit",
    },
  ],
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter: llmAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};


// coagents-research-canvas/ui/src/app/page.tsx

"use client";

import { CopilotKit } from "@copilotkit/react-core";
import Main from "./Main";
import {
  ModelSelectorProvider,
  useModelSelectorContext,
} from "@/lib/model-selector-provider";
import { ModelSelector } from "@/components/ModelSelector";
export default function ModelSelectorWrapper() {
  return (
    <ModelSelectorProvider>
      <Home />
      <ModelSelector />
    </ModelSelectorProvider>
  );
}

function Home() {
  const { agentName } = useModelSelectorContext(); // Now accessing agentName

  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      showDevConsole={false}
      agent={agentName} // Pass agentName from context
    >
      <Main />
    </CopilotKit>
  );
}


// coagents-research-canvas/ui/src/components/AddResourceDialog.tsx

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { PlusCircle, Plus } from "lucide-react";
import { Resource } from "@/lib/types";
import { Select, SelectContent, SelectGroup, SelectLabel, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

type AddResourceDialogProps = {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  newResource: Resource;
  setNewResource: (resource: Resource) => void;
  addResource: () => void;
};

export function AddResourceDialog({
  isOpen,
  onOpenChange,
  newResource,
  setNewResource,
  addResource,
}: AddResourceDialogProps) {
  const availableNamespaces = ["Namespace1", "Namespace2"]; // Replace with dynamic namespaces if available

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogTrigger asChild>
        <Button
          variant="link"
          size="sm"
          className="text-sm font-bold text-[#6766FC]"
        >
          Add Resource <PlusCircle className="w-6 h-6 ml-2" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add New Resource</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <label htmlFor="new-namespace" className="text-sm font-bold">
            Namespace
          </label>
          <Select
            value={newResource.namespace}
            onValueChange={(value) => setNewResource({ ...newResource, namespace: value })}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select Namespace" />
            </SelectTrigger>
            <SelectContent>
              {availableNamespaces.map((ns) => (
                <SelectItem key={ns} value={ns}>
                  {ns}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <label htmlFor="new-url" className="text-sm font-bold">
            Resource URL
          </label>
          <Input
            id="new-url"
            placeholder="Resource URL"
            value={newResource.url || ""}
            onChange={(e) =>
              setNewResource({ ...newResource, url: e.target.value })
            }
            aria-label="New resource URL"
            className="bg-background"
          />
          <label htmlFor="new-title" className="text-sm font-bold">
            Resource Title
          </label>
          <Input
            id="new-title"
            placeholder="Resource Title"
            value={newResource.title || ""}
            onChange={(e) =>
              setNewResource({ ...newResource, title: e.target.value })
            }
            aria-label="New resource title"
            className="bg-background"
          />
          <label htmlFor="new-description" className="text-sm font-bold">
            Resource Description
          </label>
          <Textarea
            id="new-description"
            placeholder="Resource Description"
            value={newResource.description || ""}
            onChange={(e) =>
              setNewResource({
                ...newResource,
                description: e.target.value,
              })
            }
            aria-label="New resource description"
            className="bg-background"
          />
        </div>
        <Button
          onClick={addResource}
          className="w-full bg-[#6766FC] text-white"
          disabled={
            !newResource.url ||
            !newResource.title ||
            !newResource.description ||
            !newResource.namespace
          }
        >
          <Plus className="w-4 h-4 mr-2" /> Add Resource
        </Button>
      </DialogContent>
    </Dialog>
  );
}


// coagents-research-canvas/ui/src/components/ArxivSearchDialog.tsx

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
  } from "@/components/ui/dialog";
  import { Input } from "@/components/ui/input";
  import { Button } from "@/components/ui/button";
  import { useState } from "react";
  
  type ArxivSearchDialogProps = {
    performArxivSearch: (query: string) => void;
  };
  
  export function ArxivSearchDialog({ performArxivSearch }: ArxivSearchDialogProps) {
    const [query, setQuery] = useState("");
  
    const handleSearch = () => {
      performArxivSearch(query);
    };
  
    return (
      <Dialog>
        <DialogTrigger asChild>
          <Button variant="outline" size="sm" className="mb-4 ml-4">
            Search arXiv
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Search arXiv</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <Input
              placeholder="Enter your search query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Arxiv search query"
            />
          </div>
          <Button
            onClick={handleSearch}
            className="w-full bg-[#6766FC] text-white"
            disabled={!query.trim()}
          >
            Search
          </Button>
        </DialogContent>
      </Dialog>
    );
  }
  

  // coagents-research-canvas/ui/src/components/DocumentSelectionDialog.tsx

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Resource } from "@/lib/types";

type DocumentSelectionDialogProps = {
  availableDocuments: Resource[];
  selectedDocuments: Resource[];
  setSelectedDocuments: (docs: Resource[]) => void;
};

export function DocumentSelectionDialog({
  availableDocuments,
  selectedDocuments,
  setSelectedDocuments,
}: DocumentSelectionDialogProps) {
  const [tempSelected, setTempSelected] = useState<string[]>(
    selectedDocuments.map((doc) => doc.id)
  );

  const toggleSelection = (id: string) => {
    setTempSelected((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const confirmSelection = () => {
    const docs = availableDocuments.filter((doc) =>
      tempSelected.includes(doc.id)
    );
    setSelectedDocuments(docs);
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="mb-4">
          Select Documents
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Select Documents for Research</DialogTitle>
        </DialogHeader>
        <div className="py-4">
          {availableDocuments.map((doc) => {
            // Skip documents with missing id or title
            if (!doc.id || !doc.title) {
              return null;
            }
            return (
              <div key={doc.id} className="flex items-center mb-2">
                <Checkbox
                  checked={tempSelected.includes(doc.id)}
                  onChange={() => toggleSelection(doc.id)}
                />
                <span className="ml-2">{doc.title}</span>
              </div>
            );
          })}
        </div>
        <Button
          onClick={confirmSelection}
          className="w-full bg-[#6766FC] text-white"
          disabled={tempSelected.length === 0}
        >
          Confirm Selection
        </Button>
      </DialogContent>
    </Dialog>
  );
}


// coagents-research-canvas/ui/src/components/EditResourceDialog.tsx

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Resource } from "@/lib/types";
import { Select, SelectContent, SelectGroup, SelectLabel, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

type EditResourceDialogProps = {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  editResource: Resource | null;
  setEditResource: (
    resource: ((prev: Resource | null) => Resource | null) | Resource | null
  ) => void;
  updateResource: () => void;
};

export function EditResourceDialog({
  isOpen,
  onOpenChange,
  editResource,
  setEditResource,
  updateResource,
}: EditResourceDialogProps) {
  const availableNamespaces = ["Namespace1", "Namespace2"]; // Replace with dynamic namespaces if available

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Resource</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <label htmlFor="edit-namespace" className="text-sm font-bold">
            Namespace
          </label>
          <Select
            value={editResource?.namespace || ""}
            onValueChange={(value) => setEditResource((prev) =>
              prev ? { ...prev, namespace: value } : null
            )}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select Namespace" />
            </SelectTrigger>
            <SelectContent>
              {availableNamespaces.map((ns) => (
                <SelectItem key={ns} value={ns}>
                  {ns}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <label htmlFor="edit-url" className="text-sm font-bold">
            Resource URL
          </label>
          <Input
            id="edit-url"
            placeholder="Resource URL"
            value={editResource?.url || ""}
            onChange={(e) =>
              setEditResource((prev) =>
                prev ? { ...prev, url: e.target.value } : null
              )
            }
            aria-label="Edit resource URL"
            className="bg-background"
          />
          <label htmlFor="edit-title" className="text-sm font-bold">
            Resource Title
          </label>
          <Input
            id="edit-title"
            placeholder="Resource Title"
            value={editResource?.title || ""}
            onChange={(e) =>
              setEditResource((prev: any) =>
                prev ? { ...prev, title: e.target.value } : null
              )
            }
            aria-label="Edit resource title"
            className="bg-background"
          />
          <label htmlFor="edit-description" className="text-sm font-bold">
            Resource Description
          </label>
          <Textarea
            id="edit-description"
            placeholder="Resource Description"
            value={editResource?.description || ""}
            onChange={(e) =>
              setEditResource((prev) =>
                prev ? { ...prev, description: e.target.value } : null
              )
            }
            aria-label="Edit resource description"
            className="bg-background"
          />
        </div>
        <Button
          onClick={updateResource}
          className="w-full bg-[#6766FC] text-white"
          disabled={
            !editResource?.url ||
            !editResource?.title ||
            !editResource?.description ||
            !editResource?.namespace
          }
        >
          Save Changes
        </Button>
      </DialogContent>
    </Dialog>
  );
}


// coagents-research-canvas/ui/src/components/ModelSelector.tsx
"use client"

import React from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useModelSelectorContext } from "@/lib/model-selector-provider";

export function ModelSelector() {
  const { model, setModel } = useModelSelectorContext();

  return (
    <div className="fixed bottom-0 left-0 p-4 z-50">
      <Select value={model} onValueChange={v => setModel(v)}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Theme" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="openai">OpenAI</SelectItem>
          <SelectItem value="anthropic">Anthropic</SelectItem>
          {/* <SelectItem value="google_genai">Google Generative AI</SelectItem> */}
        </SelectContent>
      </Select>
    </div>
  )
}


// coagents-research-canvas/ui/src/components/NamespaceSelector.tsx

"use client";

import React, { useEffect, useState } from "react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectLabel,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Resource } from "@/lib/types";
import axios from "axios";
import { Spinner } from "@/components/ui/spinner";

type NamespaceDocuments = {
  [namespace: string]: Resource[];
};

type NamespaceSelectorProps = {
  onSelectDocument: (document: Resource) => void;
};

export function NamespaceSelector({ onSelectDocument }: NamespaceSelectorProps) {
  const [namespaces, setNamespaces] = useState<NamespaceDocuments>({});
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDocuments = async () => {
      setLoading(true);
      try {
        const response = await axios.get<NamespaceDocuments>("http://localhost:8000/api/documents");
// const response = await axios.get<NamespaceDocuments>("/api/documents");
        setNamespaces(response.data);
      } catch (err: any) {
        setError(err.message || "Failed to fetch documents.");
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, []);

  if (loading) return <Spinner />;
  if (error) return <div className="text-red-500">Error: {error}</div>;

  return (
    <Select
      onValueChange={(value) => {
        // Find the selected document based on the ID
        for (const namespace in namespaces) {
          const doc = namespaces[namespace].find((doc) => doc.id === value);
          if (doc) {
            onSelectDocument(doc);
            break;
          }
        }
      }}
    >
      <SelectTrigger className="w-full">
        <SelectValue placeholder="Select a document" />
      </SelectTrigger>
      <SelectContent>
        {Object.keys(namespaces).map((namespace) => (
          <SelectGroup key={namespace}>
            <SelectLabel>{namespace}</SelectLabel>
            {namespaces[namespace].map((doc) => {
              if (!doc.id || !doc.title) {
                return null;
              }
              return (
                <SelectItem key={doc.id} value={doc.id}>
                  {doc.title}
                </SelectItem>
              );
            })}
          </SelectGroup>
        ))}
      </SelectContent>
    </Select>
  );
}


// coagents-research-canvas/ui/src/components/Progress.tsx
import { cn } from "@/lib/utils";
import { CheckIcon, LoaderCircle } from "lucide-react";
import { truncateUrl } from "@/lib/utils";

export function Progress({
  logs,
}: {
  logs: {
    message: string;
    done: boolean;
  }[];
}) {
  if (logs.length === 0) {
    return null;
  }

  return (
    <div>
      <div className="border border-slate-200 bg-slate-100/30 shadow-md rounded-lg overflow-hidden text-sm py-2">
        {logs.map((log, index) => (
          <div
            key={index}
            className={`flex ${
              log.done || index === logs.findIndex((log) => !log.done)
                ? ""
                : "opacity-50"
            }`}
          >
            <div className="w-8">
              <div className="w-4 h-4 bg-slate-700 flex items-center justify-center rounded-full mt-[10px] ml-[12px]">
                {log.done ? (
                  <CheckIcon className="w-3 h-3 text-white" />
                ) : (
                  <LoaderCircle className="w-3 h-3 text-white animate-spin" />
                )}
              </div>
              {index < logs.length - 1 && (
                <div
                  className={cn("h-full w-[1px] bg-slate-200 ml-[20px]")}
                ></div>
              )}
            </div>
            <div className="flex-1 flex justify-center py-2 pl-2 pr-4">
              <div className="flex-1 flex items-center text-xs">
                {log.message.replace(
                  /https?:\/\/[^\s]+/g, // Regex to match URLs
                  (url) => truncateUrl(url) // Replace with truncated URL
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


// coagents-research-canvas/ui/src/components/Progress.tsx
import { cn } from "@/lib/utils";
import { CheckIcon, LoaderCircle } from "lucide-react";
import { truncateUrl } from "@/lib/utils";

export function Progress({
  logs,
}: {
  logs: {
    message: string;
    done: boolean;
  }[];
}) {
  if (logs.length === 0) {
    return null;
  }

  return (
    <div>
      <div className="border border-slate-200 bg-slate-100/30 shadow-md rounded-lg overflow-hidden text-sm py-2">
        {logs.map((log, index) => (
          <div
            key={index}
            className={`flex ${
              log.done || index === logs.findIndex((log) => !log.done)
                ? ""
                : "opacity-50"
            }`}
          >
            <div className="w-8">
              <div className="w-4 h-4 bg-slate-700 flex items-center justify-center rounded-full mt-[10px] ml-[12px]">
                {log.done ? (
                  <CheckIcon className="w-3 h-3 text-white" />
                ) : (
                  <LoaderCircle className="w-3 h-3 text-white animate-spin" />
                )}
              </div>
              {index < logs.length - 1 && (
                <div
                  className={cn("h-full w-[1px] bg-slate-200 ml-[20px]")}
                ></div>
              )}
            </div>
            <div className="flex-1 flex justify-center py-2 pl-2 pr-4">
              <div className="flex-1 flex items-center text-xs">
                {log.message.replace(
                  /https?:\/\/[^\s]+/g, // Regex to match URLs
                  (url) => truncateUrl(url) // Replace with truncated URL
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


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
import { AgentState, Resource, ResearchSession, DeleteResourcesArgs } from "@/lib/types";

export function ResearchCanvas() {
  const { model, agent } = useModelSelectorContext();

  const { state, setState } = useCoAgent<AgentState>({
    name: "researchAgent", // Use a string identifier
    initialState: {
      model,
      research_question: "",
      report: "",
      resources: [],
      logs: [],
    },
  });

  useCoAgentStateRender({
    name: "researchAgent", // Use the same string identifier
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
    title: "",
    description: "",
    namespace: "",
  });
  const [isAddResourceOpen, setIsAddResourceOpen] = useState(false);

  const addResource = () => {
    if (
      newResource.id &&
      newResource.title &&
      newResource.description &&
      newResource.namespace
    ) {
      setResources([...resources, { ...newResource }]);
      setNewResource({ id: "", title: "", description: "", namespace: "" });
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
    setEditResource({ ...resource }); // Ensure a new object is created
    setOriginalUrl(resource.id); // Store the original URL
    setIsEditResourceOpen(true);
  };

  const updateResource = () => {
    if (editResource && originalUrl) {
      setResources(
        resources.map((resource) =>
          resource.url === originalUrl ? { ...editResource } : resource
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
    // Trigger the ArxivSearch action via CopilotKit
    await agent.invokeAction("ArxivSearch", { query });
  };

  const performWebSearch = async (query: string) => {
    // Trigger the WebSearch action via CopilotKit
    await agent.invokeAction("Search", { queries: [query] });
  };

  // Q&A Handlers
  const [qaResponses, setQaResponses] = useState<Record<string, Record<string, string>>>({}); // { [docUrl]: { [question]: answer } }

  const askQuestion = (docUrl: string, question: string): void => {
    // Find the document to get the namespace
    const doc = selectedDocuments.find((d) => d.url === docUrl);
    if (!doc) {
      console.error("Document not found for Q&A.");
      return;
    }
    const namespace = doc.namespace;

    // Handle asynchronous action within the function
    (async () => {
      try {
        // Trigger the RAG action via CopilotKit
        await agent.invokeAction("RAG", { query: question, namespace });

        // Simulate handling the response
        const answer = "This is a simulated answer based on the document.";
        setQaResponses((prev) => ({
          ...prev,
          [docUrl]: {
            ...(prev[docUrl] || {}),
            [question]: answer,
          },
        }));
      } catch (error) {
        console.error("Error asking question:", error);
        // Optionally, set an error state to display to the user
      }
    })();
  };

  // Saving Research Sessions
  const saveSession = () => {
    const session: ResearchSession = {
      model, // Current model
      research_question: state.research_question,
      selected_documents: selectedDocuments,
      resources: resources,
      report: state.report,
      qa_responses: qaResponses,
      logs: state.logs || [], // Include logs
      timestamp: new Date().toISOString(),
    };

    // Save to local storage or send to backend
    const existingSessions = JSON.parse(localStorage.getItem("research_sessions") || "[]");
    existingSessions.push(session);
    localStorage.setItem("research_sessions", JSON.stringify(existingSessions));

    alert("Research session saved successfully!");
  };

  // Load Session Handler
  const loadSession = (session: ResearchSession) => {
    setState({
      model: session.model || state.model, // Use existing model or session's model
      research_question: session.research_question,
      resources: session.resources,
      report: session.report,
      logs: session.logs || [], // Include logs
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
                if (!selectedDocuments.find((d) => d.url === doc.url)) {
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
                  key={doc.url}
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
            onChange={(e) =>
              setState({ ...state, report: e.target.value })
            }
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



// coagents-research-canvas/ui/src/components/Resources.tsx

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";
import { Resource } from "@/lib/types";

type ResourcesProps = {
  resources: Resource[];
  customWidth?: number;
  handleCardClick?: (resource: Resource) => void;
  removeResource?: (id: string) => void; // Changed parameter from url to id
};

export function Resources({
  resources,
  handleCardClick,
  removeResource,
  customWidth,
}: ResourcesProps) {
  return (
    <div className="flex space-x-3 overflow-x-auto">
      {resources.map((resource) => {
        // Skip resources without an id
        if (!resource.id) {
          return null;
        }
        return (
          <Card
            key={resource.id} // Use id as the key
            className={
              "bg-background border-0 shadow-none rounded-xl text-md font-extralight focus-visible:ring-0 flex-none" +
              (handleCardClick ? " cursor-pointer" : "")
            }
            style={{ width: customWidth ? customWidth + "px" : "320px" }}
            onClick={() => handleCardClick?.(resource)}
          >
            <CardContent className="px-6 py-6 relative">
              <div className="flex items-start space-x-3 text-sm">
                <div className="flex-grow">
                  <h3
                    className="font-bold text-lg"
                    style={{
                      maxWidth: customWidth ? customWidth - 30 + "px" : "230px",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {resource.title || "Untitled"}
                  </h3>
                  <p
                    className="text-base mt-2"
                    style={{
                      maxWidth: customWidth ? customWidth - 30 + "px" : "250px",
                      overflowWrap: "break-word",
                    }}
                  >
                    {resource.description?.length > 250
                      ? resource.description.slice(0, 250) + "..."
                      : resource.description}
                  </p>
                  {/* Optionally display the namespace or other properties */}
                  <p className="text-sm text-gray-500 mt-2">
                    Namespace: {resource.namespace}
                  </p>
                </div>
                {removeResource && (
                  <div className="flex items-start absolute top-4 right-4">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeResource(resource.id);
                      }}
                      aria-label={`Remove ${resource.title || resource.id}`}
                    >
                      <Trash2 className="w-6 h-6 text-gray-400 hover:text-red-500" />
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}


// coagents-research-canvas/ui/src/components/SavedSessions.tsx

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ResearchSession, useResearchSessions } from "@/lib/session";

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
// coagents-research-canvas/ui/src/components/WebSearchDialog.tsx

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
  } from "@/components/ui/dialog";
  import { Input } from "@/components/ui/input";
  import { Button } from "@/components/ui/button";
  import { useState } from "react";
  
  type WebSearchDialogProps = {
    performWebSearch: (query: string) => void;
  };
  
  export function WebSearchDialog({ performWebSearch }: WebSearchDialogProps) {
    const [query, setQuery] = useState("");
  
    const handleSearch = () => {
      performWebSearch(query);
    };
  
    return (
      <Dialog>
        <DialogTrigger asChild>
          <Button variant="outline" size="sm" className="mb-4 ml-4">
            Web Search
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Web Search</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <Input
              placeholder="Enter your search query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Web search query"
            />
          </div>
          <Button
            onClick={handleSearch}
            className="w-full bg-[#6766FC] text-white"
            disabled={!query.trim()}
          >
            Search
          </Button>
        </DialogContent>
      </Dialog>
    );
  }
  
