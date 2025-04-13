// File: abts-generator/src/app/questions/[id]/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { MainLayout } from "@/components/layout/main-layout";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Trash2, Edit, BookCopy } from "lucide-react";
import { questionsApi, Question } from "@/lib/api";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatDate } from "@/lib/utils";

export default function QuestionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [question, setQuestion] = useState<Question | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const fetchQuestion = async () => {
      if (!params.id) return;
      
      try {
        setLoading(true);
        const questionData = await questionsApi.getQuestion(params.id as string);
        setQuestion(questionData);
      } catch (error) {
        console.error("Error fetching question:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestion();
  }, [params.id]);

  const handleDelete = async () => {
    if (!question || deleting) return;
    
    if (!confirm("Are you sure you want to delete this question?")) {
      return;
    }
    
    try {
      setDeleting(true);
      await questionsApi.deleteQuestion(question.id);
      router.push("/questions");
    } catch (error) {
      console.error("Error deleting question:", error);
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[50vh]">
          <p>Loading question...</p>
        </div>
      </MainLayout>
    );
  }

  if (!question) {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center min-h-[50vh]">
          <p className="text-xl mb-4">Question not found</p>
          <Link href="/questions">
            <Button>Back to Questions</Button>
          </Link>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="mb-6">
        <Link href="/questions">
          <Button variant="ghost" className="flex items-center gap-2 pl-0">
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Questions</span>
          </Button>
        </Link>
      </div>

      <PageHeader
        title="Question Details"
        description={`Created: ${formatDate(question.created_at)}`}
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              className="flex items-center gap-2"
              onClick={() => {
                navigator.clipboard.writeText(question.text);
                alert("Question copied to clipboard");
              }}
            >
              <BookCopy className="h-4 w-4" />
              <span>Copy</span>
            </Button>
            <Link href={`/questions/${question.id}/edit`}>
              <Button variant="outline" className="flex items-center gap-2">
                <Edit className="h-4 w-4" />
                <span>Edit</span>
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
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Question</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="p-4 rounded-md bg-muted/50">
                <p className="font-medium text-lg">{question.text}</p>
              </div>
            </CardContent>
          </Card>
          
          {question.options && question.options.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Answer Options</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {question.options.map((option) => (
                    <li 
                      key={option.id} 
                      className={`p-3 rounded-md border ${
                        option.is_correct 
                          ? "border-green-200 bg-green-50 dark:bg-green-950/20 dark:border-green-900" 
                          : "border-border bg-muted/30"
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`flex items-center justify-center w-6 h-6 rounded-full shrink-0 mt-0.5 ${
                          option.is_correct 
                            ? "bg-green-500 text-white" 
                            : "bg-muted border border-muted-foreground/30"
                          }`}
                        >
                          {option.is_correct && "✓"}
                        </div>
                        <span>{option.text}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
          
          {question.explanation && (
            <Card>
              <CardHeader>
                <CardTitle>Explanation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="p-4 rounded-md bg-muted/50">
                  <p>{question.explanation}</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
        
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Metadata</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="space-y-2">
                {question.domain && (
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Domain</dt>
                    <dd>{question.domain}</dd>
                  </div>
                )}
                
                {question.cognitive_complexity && (
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Cognitive Complexity</dt>
                    <dd>{question.cognitive_complexity}</dd>
                  </div>
                )}
                
                {question.blooms_taxonomy_level && (
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Bloom's Taxonomy Level</dt>
                    <dd>{question.blooms_taxonomy_level}</dd>
                  </div>
                )}
                
                {question.question_type && (
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Question Type</dt>
                    <dd>{question.question_type.replace('-', ' ')}</dd>
                  </div>
                )}
                
                {question.surgically_appropriate !== undefined && (
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Surgically Appropriate</dt>
                    <dd>{question.surgically_appropriate ? "Yes" : "No"}</dd>
                  </div>
                )}
              </dl>
            </CardContent>
          </Card>
          
          {question.outline_id && (
            <Card>
              <CardHeader>
                <CardTitle>Content Outline</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">
                  This question is linked to a content outline.
                </p>
              </CardContent>
              <CardFooter>
                <Link href={`/outlines/${question.outline_id}`} className="w-full">
                  <Button variant="outline" className="w-full">
                    View Content Outline
                  </Button>
                </Link>
              </CardFooter>
            </Card>
          )}
          
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Link href={`/questions/${question.id}/edit`} className="w-full">
                <Button variant="outline" className="w-full">
                  Edit Question
                </Button>
              </Link>
              <Link href={`/comparisons/create?questionId=${question.id}`} className="w-full">
                <Button className="w-full">
                  Create Comparison
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}