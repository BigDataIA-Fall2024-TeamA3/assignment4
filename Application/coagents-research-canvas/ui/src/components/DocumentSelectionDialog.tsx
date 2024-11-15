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
