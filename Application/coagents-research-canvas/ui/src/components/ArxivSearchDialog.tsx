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
  