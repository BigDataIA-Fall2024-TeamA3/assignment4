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
