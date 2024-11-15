# frontend code files

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
      // url: process.env.REMOTE_ACTION_URL || "http://localhost:8000/copilotkit",
      url: "http://localhost:8000/copilotkit"
      // url: "https://sm2vrgnlj5aq57hbcd3xjlg2c40grcwk.lambda-url.us-east-1.on.aws/copilotkit"
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
            !newResource.url || !newResource.title || !newResource.description
          }
        >
          <Plus className="w-4 h-4 mr-2" /> Add Resource
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
  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Resource</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
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
            !editResource?.description
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
import { AgentState, Resource } from "@/lib/types";
import { useModelSelectorContext } from "@/lib/model-selector-provider";

export function ResearchCanvas() {
  const { model, agent } = useModelSelectorContext();

  const { state, setState } = useCoAgent<AgentState>({
    name: agent,
    initialState: {
      model,
    },
  });

  useCoAgentStateRender({
    name: agent,
    render: ({ state, nodeName, status }) => {
      if (!state.logs || state.logs.length === 0) {
        return null;
      }
      return <Progress logs={state.logs} />;
    },
  });

  useCopilotAction({
    name: "DeleteResources",
    disabled: true,
    parameters: [
      {
        name: "urls",
        type: "string[]",
      },
    ],
    renderAndWait: ({ args, status, handler }) => {
      return (
        <div className="">
          <div className="font-bold text-base mb-2">
            Delete these resources?
          </div>
          <Resources
            resources={resources.filter((resource) =>
              (args.urls || []).includes(resource.url)
            )}
            customWidth={200}
          />
          {status === "executing" && (
            <div className="mt-4 flex justify-start space-x-2">
              <button
                onClick={() => handler("NO")}
                className="px-4 py-2 text-[#6766FC] border border-[#6766FC] rounded text-sm font-bold"
              >
                Cancel
              </button>
              <button
                onClick={() => handler("YES")}
                className="px-4 py-2 bg-[#6766FC] text-white rounded text-sm font-bold"
              >
                Delete
              </button>
            </div>
          )}
        </div>
      );
    },
  });

  const resources: Resource[] = state.resources || [];
  const setResources = (resources: Resource[]) => {
    setState({ ...state, resources });
  };

  // const [resources, setResources] = useState<Resource[]>(dummyResources);
  const [newResource, setNewResource] = useState<Resource>({
    url: "",
    title: "",
    description: "",
  });
  const [isAddResourceOpen, setIsAddResourceOpen] = useState(false);

  const addResource = () => {
    if (newResource.url) {
      setResources([...resources, { ...newResource }]);
      setNewResource({ url: "", title: "", description: "" });
      setIsAddResourceOpen(false);
    }
  };

  const removeResource = (url: string) => {
    setResources(
      resources.filter((resource: Resource) => resource.url !== url)
    );
  };

  const [editResource, setEditResource] = useState<Resource | null>(null);
  const [originalUrl, setOriginalUrl] = useState<string | null>(null);
  const [isEditResourceOpen, setIsEditResourceOpen] = useState(false);

  const handleCardClick = (resource: Resource) => {
    setEditResource({ ...resource }); // Ensure a new object is created
    setOriginalUrl(resource.url); // Store the original URL
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

  return (
    <div className="container w-full h-full p-10 bg-[#F5F8FF]">
      <div className="space-y-8">
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

        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-medium text-primary">Resources</h2>
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
      </div>
    </div>
  );
}


// coagents-research-canvas/ui/src/components/Resources.tsx
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";
import { Resource } from "@/lib/types";
import { truncateUrl } from "@/lib/utils";

type ResourcesProps = {
  resources: Resource[];
  customWidth?: number;
  handleCardClick?: (resource: Resource) => void;
  removeResource?: (url: string) => void;
};

export function Resources({
  resources,
  handleCardClick,
  removeResource,
  customWidth,
}: ResourcesProps) {
  return (
    <div className="flex space-x-3 overflow-x-auto">
      {resources.map((resource) => (
        <Card
          key={resource.url} // Use url as the key
          className={
            "bg-background border-0 shadow-none rounded-xl text-md font-extralight focus-visible:ring-0 flex-none" +
            (handleCardClick ? " cursor-pointer" : "")
          }
          style={{ width: customWidth + "px" || "320px" }}
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
                  {resource.title}
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
                <a
                  href={resource.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary hover:underline mt-3 text-slate-400 inline-block"
                  title={resource.url}
                  style={{
                    width: customWidth ? customWidth - 30 + "px" : "250px",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  <img
                    src={`https://www.google.com/s2/favicons?domain=${resource.url}`}
                    alt="favicon"
                    className="inline-block mr-2"
                    style={{ width: "16px", height: "16px" }}
                  />
                  {truncateUrl(resource.url)}
                </a>
              </div>
              {removeResource && (
                <div className="flex items-start absolute top-4 right-4">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeResource?.(resource.url);
                    }}
                    aria-label={`Remove ${resource.url}`}
                  >
                    <Trash2 className="w-6 h-6 text-gray-400 hover:text-red-500" />
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}


