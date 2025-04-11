// File: abts-generator/src/app/templates/[id]/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { MainLayout } from "@/components/layout/main-layout";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Trash2, Edit, Beaker } from "lucide-react";
import { templatesApi, Template } from "@/lib/api";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TemplateForm } from "@/components/template/template-form";

export default function TemplateDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [template, setTemplate] = useState<Template | null>(null);
  const [loading, setLoading] = useState(true);
  const [processingForm, setProcessingForm] = useState(false);
  const [previewResult, setPreviewResult] = useState<any>(null);

  useEffect(() => {
    const fetchTemplate = async () => {
      if (!params.id) return;
      
      try {
        setLoading(true);
        const templateData = await templatesApi.getTemplate(params.id as string);
        setTemplate(templateData);
      } catch (error) {
        console.error("Error fetching template:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTemplate();
  }, [params.id]);

  const handlePreview = async (formValues: Record<string, any>) => {
    if (!template || processingForm) return;
    
    try {
      setProcessingForm(true);
      const result = await templatesApi.renderTemplate(template.id, formValues);
      setPreviewResult(result);
    } catch (error) {
      console.error("Error rendering template:", error);
      alert("Error rendering template. Please check your inputs and try again.");
    } finally {
      setProcessingForm(false);
    }
  };

  const handleGenerate = async (formValues: Record<string, any>) => {
    if (!template || processingForm) return;
    
    try {
      setProcessingForm(true);
      // In a real implementation, this would create questions
      router.push(`/generate?templateId=${template.id}`);
    } catch (error) {
      console.error("Error generating questions:", error);
      setProcessingForm(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[50vh]">
          <p>Loading template...</p>
        </div>
      </MainLayout>
    );
  }

  if (!template) {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center min-h-[50vh]">
          <p className="text-xl mb-4">Template not found</p>
          <Link href="/templates">
            <Button>Back to Templates</Button>
          </Link>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="mb-6">
        <Link href="/templates">
          <Button variant="ghost" className="flex items-center gap-2 pl-0">
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Templates</span>
          </Button>
        </Link>
      </div>

      <PageHeader
        title={template.id}
        description={`Template type: ${template.type}`}
        actions={
          <div className="flex items-center gap-2">
            <Link href={`/templates/${template.id}/edit`}>
              <Button variant="outline" className="flex items-center gap-2">
                <Edit className="h-4 w-4" />
                <span>Edit</span>
              </Button>
            </Link>
            <Link href={`/generate?templateId=${template.id}`}>
              <Button className="flex items-center gap-2">
                <Beaker className="h-4 w-4" />
                <span>Generate Questions</span>
              </Button>
            </Link>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Template</CardTitle>
            {template.description && (
              <CardDescription>
                {template.description}
              </CardDescription>
            )}
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="form">
              <TabsList className="mb-4">
                <TabsTrigger value="form">Template Form</TabsTrigger>
                <TabsTrigger value="preview" disabled={!previewResult}>Preview Result</TabsTrigger>
              </TabsList>
              
              <TabsContent value="form">
                <div className="space-y-6">
                  <TemplateForm 
                    template={template} 
                    onSubmit={handlePreview}
                    isLoading={processingForm}
                  />
                </div>
              </TabsContent>
              
              <TabsContent value="preview">
                {previewResult && (
                  <div className="border rounded-md p-4">
                    <h3 className="text-lg font-semibold mb-3">Generated Question</h3>
                    
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-2">Question</h4>
                        <p>{previewResult.text}</p>
                      </div>
                      
                      {previewResult.options && (
                        <div>
                          <h4 className="font-medium mb-2">Options</h4>
                          <ul className="space-y-2">
                            {previewResult.options.map((option: any, index: number) => (
                              <li 
                                key={index} 
                                className={`${
                                  option.isCorrect || option.is_correct
                                    ? "text-green-600 dark:text-green-400" 
                                    : ""
                                }`}
                              >
                                {option.text} {option.isCorrect || option.is_correct ? "(Correct)" : ""}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {previewResult.explanation && (
                        <div>
                          <h4 className="font-medium mb-2">Explanation</h4>
                          <p>{previewResult.explanation}</p>
                        </div>
                      )}
                    </div>
                    
                    <div className="mt-6">
                      <Button 
                        onClick={() => handleGenerate(previewResult)}
                        disabled={processingForm}
                      >
                        Generate Using This Template
                      </Button>
                    </div>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
        
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Template Details</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="space-y-2">
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">ID</dt>
                  <dd>{template.id}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Type</dt>
                  <dd>{template.type}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Variables</dt>
                  <dd className="flex flex-wrap gap-1 mt-1">
                    {template.variables.map(variable => (
                      <span
                        key={variable}
                        className="inline-flex items-center rounded-full bg-muted px-2.5 py-0.5 text-xs font-semibold"
                      >
                        {variable}
                      </span>
                    ))}
                  </dd>
                </div>
                {template.has_conditionals && (
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Conditionals</dt>
                    <dd>This template contains conditional logic</dd>
                  </div>
                )}
              </dl>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Usage Instructions</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Fill in the template variables in the form on the left to generate a question preview.
              </p>
              
              {template.required_variables && template.required_variables.length > 0 && (
                <div className="mt-2">
                  <h4 className="text-sm font-medium mb-1">Required Variables:</h4>
                  <ul className="text-sm pl-5 list-disc">
                    {template.required_variables.map(variable => (
                      <li key={variable}>{variable}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {template.optional_variables && template.optional_variables.length > 0 && (
                <div className="mt-2">
                  <h4 className="text-sm font-medium mb-1">Optional Variables:</h4>
                  <ul className="text-sm pl-5 list-disc">
                    {template.optional_variables.map(variable => (
                      <li key={variable}>{variable}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
            <CardFooter>
              <Link href={`/generate?templateId=${template.id}`} className="w-full">
                <Button variant="outline" className="w-full">
                  Use in Question Generator
                </Button>
              </Link>
            </CardFooter>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}