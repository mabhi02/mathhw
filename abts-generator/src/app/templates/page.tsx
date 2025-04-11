// File: abts-generator/src/app/templates/page.tsx
"use client";

import { useState, useEffect } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { PageHeader } from "@/components/layout/page-header";
import { TemplateCard } from "@/components/template/template-card";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import Link from "next/link";
import { templatesApi, Template } from "@/lib/api";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState("");
  const [uniqueTypes, setUniqueTypes] = useState<string[]>([]);

  useEffect(() => {
    const loadTemplates = async () => {
      try {
        setLoading(true);
        const data = await templatesApi.getTemplates();
        setTemplates(data);
        
        // Extract unique template types
        const types = Array.from(new Set(data.map(t => t.type)));
        setUniqueTypes(types);
      } catch (error) {
        console.error("Error loading templates:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadTemplates();
  }, []);

  // Filter templates by type if selected
  const filteredTemplates = selectedType 
    ? templates.filter(t => t.type === selectedType)
    : templates;

  return (
    <MainLayout>
      <PageHeader
        title="Question Templates"
        description="Browse and use templates for generating questions"
        actions={
          <Link href="/templates/create">
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              <span>New Template</span>
            </Button>
          </Link>
        }
      />

      <div className="mb-8">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="w-full sm:w-auto">
            <Select
              value={selectedType}
              onValueChange={setSelectedType}
            >
              <SelectTrigger className="w-full sm:w-[220px]">
                <SelectValue placeholder="Filter by template type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Template Types</SelectItem>
                {uniqueTypes.map(type => (
                  <SelectItem key={type} value={type}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {selectedType && (
            <Button 
              variant="ghost" 
              onClick={() => setSelectedType("")}
              className="h-9"
            >
              Clear filter
            </Button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-center p-8">
          <p>Loading templates...</p>
        </div>
      ) : filteredTemplates.length > 0 ? (
        <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {filteredTemplates.map((template) => (
            <TemplateCard key={template.id} template={template} />
          ))}
        </div>
      ) : (
        <div className="text-center p-8 border rounded-lg bg-muted/40">
          <p>No templates found. Create a new template to get started.</p>
          <Link href="/templates/create" className="mt-4 inline-block">
            <Button>Create New Template</Button>
          </Link>
        </div>
      )}
    </MainLayout>
  );
}