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
