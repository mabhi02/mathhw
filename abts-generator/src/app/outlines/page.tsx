// File: abts-generator/src/app/outlines/page.tsx
"use client";

import { useState, useEffect } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { PageHeader } from "@/components/layout/page-header";
import { OutlineCard } from "@/components/outline/outline-card";
import { Button } from "@/components/ui/button";
import { Plus, Upload } from "lucide-react";
import Link from "next/link";
import { outlinesApi, Outline } from "@/lib/api";
import { Input } from "@/components/ui/input";

export default function OutlinesPage() {
  const [outlines, setOutlines] = useState<Outline[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const loadOutlines = async () => {
      try {
        setLoading(true);
        const data = await outlinesApi.getOutlines();
        setOutlines(data);
      } catch (error) {
        console.error("Error loading outlines:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadOutlines();
  }, []);

  // Filter outlines by search term
  const filteredOutlines = searchTerm
    ? outlines.filter(outline => 
        outline.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (outline.description && outline.description.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    : outlines;

  return (
    <MainLayout>
      <PageHeader
        title="Content Outlines"
        description="Browse and manage your content outlines for question generation"
        actions={
          <div className="flex space-x-2">
            <Link href="/outlines/upload">
              <Button variant="outline" className="flex items-center gap-2">
                <Upload className="h-4 w-4" />
                <span>Upload</span>
              </Button>
            </Link>
            <Link href="/outlines/create">
              <Button className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                <span>New Outline</span>
              </Button>
            </Link>
          </div>
        }
      />

      <div className="mb-8">
        <Input
          placeholder="Search outlines..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-md"
        />
      </div>

      {loading ? (
        <div className="text-center p-8">
          <p>Loading outlines...</p>
        </div>
      ) : filteredOutlines.length > 0 ? (
        <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {filteredOutlines.map((outline) => (
            <OutlineCard key={outline.id} outline={outline} />
          ))}
        </div>
      ) : (
        <div className="text-center p-8 border rounded-lg bg-muted/40">
          <p>No outlines found. Create a new outline to get started.</p>
          <div className="flex justify-center space-x-4 mt-4">
            <Link href="/outlines/upload">
              <Button variant="outline">Upload Outline</Button>
            </Link>
            <Link href="/outlines/create">
              <Button>Create New Outline</Button>
            </Link>
          </div>
        </div>
      )}
    </MainLayout>
  );
}