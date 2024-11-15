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
  