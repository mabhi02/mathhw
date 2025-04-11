// File: abts-generator/src/app/outlines/[id]/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { MainLayout } from "@/components/layout/main-layout";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Trash2, Edit, Beaker } from "lucide-react";
import { outlinesApi, Outline, OutlineNode } from "@/lib/api";
import Link from "next/link";
import { OutlineNodeView } from "@/components/outline/outline-node-view";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function OutlineDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [outline, setOutline] = useState<Outline | null>(null);
  const [outlineContent, setOutlineContent] = useState<OutlineNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [validating, setValidating] = useState(false);

  useEffect(() => {
    const fetchOutline = async () => {
      if (!params.id) return;
      
      try {
        setLoading(true);
        const outlineData = await outlinesApi.getOutline(params.id as string);
        setOutline(outlineData);
        setOutlineContent(outlineData.root);
      } catch (error) {
        console.error("Error fetching outline:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchOutline();
  }, [params.id]);

  const handleDelete = async () => {
    if (!outline || deleting) return;
    
    if (!confirm("Are you sure you want to delete this outline?")) {
      return;
    }
    
    try {
      setDeleting(true);
      await outlinesApi.deleteOutline(outline.id);
      router.push("/outlines");
    } catch (error) {
      console.error("Error deleting outline:", error);
      setDeleting(false);
    }
  };

  const handleValidate = async () => {
    if (!outline || validating) return;
    
    try {
      setValidating(true);
      const result = await outlinesApi.validateOutline(outline.id);
      setValidationResult(result);
    } catch (error) {
      console.error("Error validating outline:", error);
    } finally {
      setValidating(false);
    }
  };

  const handleGenerateQuestion = (node: OutlineNode) => {
    router.push(`/generate?outlineId=${outline?.id}&nodeId=${node.id}`);
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[50vh]">
          <p>Loading outline...</p>
        </div>
      </MainLayout>
    );
  }

  if (!outline || !outlineContent) {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center min-h-[50vh]">
          <p className="text-xl mb-4">Outline not found</p>
          <Link href="/outlines">
            <Button>Back to Outlines</Button>
          </Link>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="mb-6">
        <Link href="/outlines">
          <Button variant="ghost" className="flex items-center gap-2 pl-0">
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Outlines</span>
          </Button>
        </Link>
      </div>

      <PageHeader
        title={outline.title}
        description={outline.description || "No description provided"}
        actions={
          <div className="flex items-center gap-2">
            <Link href={`/outlines/${outline.id}/edit`}>
              <Button variant="outline" className="flex items-center gap-2">
                <Edit className="h-4 w-4" />
                <span>Edit</span>
              </Button>
            </Link>
            <Link href={`/generate?outlineId=${outline.id}`}>
              <Button className="flex items-center gap-2">
                <Beaker className="h-4 w-4" />
                <span>Generate Questions</span>
              </Button>
            </Link>
            <Button 
              variant="destructive" 
              className="flex items-center gap-2"
              onClick={handleDelete}
              disabled={deleting}
            >
              <Trash2 className="h-4 w-4" />
              <span>{deleting ? "Deleting..." : "Delete"}</span>
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Outline Structure</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="structure">
              <TabsList className="mb-4">
                <TabsTrigger value="structure">Structure</TabsTrigger>
                <TabsTrigger value="validation" disabled={!validationResult}>Validation Results</TabsTrigger>
              </TabsList>
              
              <TabsContent value="structure">
                <div className="border rounded-md p-4 max-h-[600px] overflow-y-auto">
                  <OutlineNodeView 
                    node={outlineContent} 
                    onGenerateQuestion={handleGenerateQuestion}
                  />
                </div>
              </TabsContent>
              
              <TabsContent value="validation">
                {validationResult && (
                  <div className="border rounded-md p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold">
                        Validation Status: {validationResult.valid ? "Valid" : "Issues Found"}
                      </h3>
                      <span className={`px-2 py-1 rounded text-sm ${
                        validationResult.valid ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                      }`}>
                        {validationResult.valid ? "Valid" : "Invalid"}
                      </span>
                    </div>
                    
                    {validationResult.issues && validationResult.issues.length > 0 && (
                      <div className="mb-4">
                        <h4 className="font-medium mb-2">Issues:</h4>
                        <ul className="list-disc pl-5 space-y-1">
                          {validationResult.issues.map((issue: string, index: number) => (
                            <li key={index} className="text-red-600">{issue}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {validationResult.warnings && validationResult.warnings.length > 0 && (
                      <div className="mb-4">
                        <h4 className="font-medium mb-2">Warnings:</h4>
                        <ul className="list-disc pl-5 space-y-1">
                          {validationResult.warnings.map((warning: string, index: number) => (
                            <li key={index} className="text-amber-600">{warning}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {validationResult.stats && (
                      <div>
                        <h4 className="font-medium mb-2">Statistics:</h4>
                        <dl className="space-y-1">
                          {Object.entries(validationResult.stats).map(([key, value]: [string, any]) => (
                            <div key={key} className="flex">
                              <dt className="w-32 font-medium text-muted-foreground capitalize">{key.replace('_', ' ')}:</dt>
                              <dd>{value}</dd>
                            </div>
                          ))}
                        </dl>
                      </div>
                    )}
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
          <CardFooter>
            <Button 
              onClick={handleValidate} 
              disabled={validating}
              variant="outline"
            >
              {validating ? "Validating..." : "Validate Outline"}
            </Button>
          </CardFooter>
        </Card>
        
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Metadata</CardTitle>
            </CardHeader>
            <CardContent>
              {outline.metadata && Object.keys(outline.metadata).length > 0 ? (
                <dl className="space-y-2">
                  {Object.entries(outline.metadata).map(([key, value]) => (
                    <div key={key}>
                      <dt className="text-sm font-medium text-muted-foreground capitalize">
                        {key.replace('_', ' ')}
                      </dt>
                      <dd>
                        {typeof value === "string" 
                          ? value 
                          : Array.isArray(value) 
                            ? value.join(", ")
                            : JSON.stringify(value)
                        }
                      </dd>
                    </div>
                  ))}
                </dl>
              ) : (
                <p className="text-sm text-muted-foreground">No metadata available</p>
              )}
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Question Generation</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Generate questions from this outline to create high-quality assessment material.
              </p>
              <p className="text-sm mb-4">
                You can generate questions from:
              </p>
              <ul className="text-sm list-disc pl-5 mb-4 space-y-1">
                <li>The entire outline</li>
                <li>Specific sections (click "Generate" next to any section)</li>
              </ul>
            </CardContent>
            <CardFooter>
              <Link href={`/generate?outlineId=${outline.id}`} className="w-full">
                <Button className="w-full">
                  Generate Questions from Outline
                </Button>
              </Link>
            </CardFooter>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}