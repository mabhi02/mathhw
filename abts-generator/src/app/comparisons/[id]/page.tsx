// File: abts-generator/src/app/comparisons/[id]/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { MainLayout } from "@/components/layout/main-layout";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Trash2, ThumbsUp, ThumbsDown } from "lucide-react";
import { comparisonsApi, feedbackApi, ComparisonResult, UserFeedback } from "@/lib/api";
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
import { Textarea } from "@/components/ui/textarea";

export default function ComparisonDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [feedback, setFeedback] = useState<UserFeedback | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  
  // Form state
  const [preferredOutput, setPreferredOutput] = useState<"direct" | "agent" | "">("");
  const [directRating, setDirectRating] = useState<number>(0);
  const [agentRating, setAgentRating] = useState<number>(0);
  const [rationale, setRationale] = useState("");
  const [additionalNotes, setAdditionalNotes] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      if (!params.id) return;
      
      try {
        setLoading(true);
        
        // Fetch comparison data
        const comparisonData = await comparisonsApi.getComparison(params.id as string);
        setComparison(comparisonData);
        
        // Try to fetch existing feedback
        try {
          const feedbackData = await feedbackApi.getFeedbackByComparison(params.id as string);
          setFeedback(feedbackData);
          
          // Populate form with existing feedback
          setPreferredOutput(feedbackData.preferred_output);
          setDirectRating(feedbackData.direct_rating || 0);
          setAgentRating(feedbackData.agent_rating || 0);
          setRationale(feedbackData.rationale || "");
          setAdditionalNotes(feedbackData.additional_notes || "");
        } catch (error) {
          // It's okay if there's no feedback yet
          console.log("No existing feedback found");
        }
      } catch (error) {
        console.error("Error fetching comparison:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [params.id]);

  const handleDelete = async () => {
    if (!comparison || deleting) return;
    
    if (!confirm("Are you sure you want to delete this comparison?")) {
      return;
    }
    
    try {
      setDeleting(true);
      await comparisonsApi.deleteComparison(comparison.id);
      router.push("/comparisons");
    } catch (error) {
      console.error("Error deleting comparison:", error);
      setDeleting(false);
    }
  };

  const handleSubmitFeedback = async () => {
    if (!comparison || !preferredOutput || submitting) return;
    
    try {
      setSubmitting(true);
      
      const feedbackData = {
        comparison_id: comparison.id,
        preferred_output: preferredOutput,
        direct_rating: directRating > 0 ? directRating : undefined,
        agent_rating: agentRating > 0 ? agentRating : undefined,
        rationale: rationale || undefined,
        additional_notes: additionalNotes || undefined
      };
      
      const result = await feedbackApi.createFeedback(feedbackData);
      setFeedback(result);
      alert("Feedback submitted successfully!");
    } catch (error) {
      console.error("Error submitting feedback:", error);
      alert("Error submitting feedback. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const renderRatingStars = (value: number, onChange: (rating: number) => void) => {
    return (
      <div className="flex space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => onChange(star)}
            className={`text-2xl ${
              value >= star ? "text-amber-500" : "text-gray-300"
            }`}
          >
            ★
          </button>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[50vh]">
          <p>Loading comparison...</p>
        </div>
      </MainLayout>
    );
  }

  if (!comparison) {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center min-h-[50vh]">
          <p className="text-xl mb-4">Comparison not found</p>
          <Link href="/comparisons">
            <Button>Back to Comparisons</Button>
          </Link>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="mb-6">
        <Link href="/comparisons">
          <Button variant="ghost" className="flex items-center gap-2 pl-0">
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Comparisons</span>
          </Button>
        </Link>
      </div>

      <PageHeader
        title="Comparison Details"
        description="Compare direct GPT-4o and agent-based generation approaches"
        actions={
          <Button 
            variant="destructive" 
            className="flex items-center gap-2"
            onClick={handleDelete}
            disabled={deleting}
          >
            <Trash2 className="h-4 w-4" />
            <span>{deleting ? "Deleting..." : "Delete"}</span>
          </Button>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Input</CardTitle>
              <CardDescription>
                Created: {formatDate(comparison.created_at)}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-4 rounded-md bg-muted/50 whitespace-pre-wrap">
                {comparison.input_text}
              </div>
            </CardContent>
          </Card>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Direct Output</CardTitle>
                <CardDescription>
                  Using GPT-4o directly
                  {comparison.direct_processing_time_ms && (
                    <span className="ml-2">
                      ({comparison.direct_processing_time_ms}ms)
                    </span>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="p-4 rounded-md bg-muted/50 whitespace-pre-wrap max-h-[400px] overflow-y-auto">
                  {comparison.direct_output}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Agent Output</CardTitle>
                <CardDescription>
                  Using agent pipeline
                  {comparison.agent_processing_time_ms && (
                    <span className="ml-2">
                      ({comparison.agent_processing_time_ms}ms)
                    </span>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="p-4 rounded-md bg-muted/50 whitespace-pre-wrap max-h-[400px] overflow-y-auto">
                  {comparison.agent_output}
                </div>
              </CardContent>
            </Card>
          </div>
          
          {!feedback ? (
            <Card>
              <CardHeader>
                <CardTitle>Provide Feedback</CardTitle>
                <CardDescription>
                  Your feedback helps improve the question generation system
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">Which output do you prefer?</h4>
                    <div className="flex gap-4">
                      <Button 
                        variant={preferredOutput === "direct" ? "default" : "outline"}
                        onClick={() => setPreferredOutput("direct")}
                        className="flex items-center gap-2"
                      >
                        <ThumbsUp className="h-4 w-4" />
                        <span>Direct Output</span>
                      </Button>
                      <Button 
                        variant={preferredOutput === "agent" ? "default" : "outline"}
                        onClick={() => setPreferredOutput("agent")}
                        className="flex items-center gap-2"
                      >
                        <ThumbsUp className="h-4 w-4" />
                        <span>Agent Output</span>
                      </Button>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">Rate Direct Output (1-5)</h4>
                      {renderRatingStars(directRating, setDirectRating)}
                    </div>
                    
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">Rate Agent Output (1-5)</h4>
                      {renderRatingStars(agentRating, setAgentRating)}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <label htmlFor="rationale" className="text-sm font-medium">
                      Why did you prefer this output?
                    </label>
                    <Textarea
                      id="rationale"
                      placeholder="Explain your preference..."
                      value={rationale}
                      onChange={(e) => setRationale(e.target.value)}
                      rows={3}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <label htmlFor="additional-notes" className="text-sm font-medium">
                      Additional Notes (Optional)
                    </label>
                    <Textarea
                      id="additional-notes"
                      placeholder="Any other comments or suggestions..."
                      value={additionalNotes}
                      onChange={(e) => setAdditionalNotes(e.target.value)}
                      rows={3}
                    />
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button 
                  onClick={handleSubmitFeedback} 
                  disabled={!preferredOutput || submitting}
                  className="w-full"
                >
                  {submitting ? "Submitting..." : "Submit Feedback"}
                </Button>
              </CardFooter>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Your Feedback</CardTitle>
                <CardDescription>
                  Submitted on {formatDate(feedback.created_at)}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 rounded-md bg-muted/50">
                    <h4 className="font-medium mb-2">Preferred Output:</h4>
                    <p className="flex items-center gap-2">
                      <ThumbsUp className="h-4 w-4 text-green-600" />
                      <span>{feedback.preferred_output === "direct" ? "Direct Output" : "Agent Output"}</span>
                    </p>
                  </div>
                  
                  {(feedback.direct_rating || feedback.agent_rating) && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {feedback.direct_rating && (
                        <div>
                          <h4 className="text-sm font-medium mb-1">Direct Output Rating:</h4>
                          <div className="flex">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <span
                                key={star}
                                className={`text-2xl ${
                                  feedback.direct_rating && feedback.direct_rating >= star ? "text-amber-500" : "text-gray-300"
                                }`}
                              >
                                ★
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {feedback.agent_rating && (
                        <div>
                          <h4 className="text-sm font-medium mb-1">Agent Output Rating:</h4>
                          <div className="flex">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <span
                                key={star}
                                className={`text-2xl ${
                                  feedback.agent_rating && feedback.agent_rating >= star ? "text-amber-500" : "text-gray-300"
                                }`}
                              >
                                ★
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {feedback.rationale && (
                    <div>
                      <h4 className="text-sm font-medium mb-1">Rationale:</h4>
                      <p className="text-sm whitespace-pre-wrap">{feedback.rationale}</p>
                    </div>
                  )}
                  
                  {feedback.additional_notes && (
                    <div>
                      <h4 className="text-sm font-medium mb-1">Additional Notes:</h4>
                      <p className="text-sm whitespace-pre-wrap">{feedback.additional_notes}</p>
                    </div>
                  )}
                </div>
              </CardContent>
              <CardFooter>
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setFeedback(null);
                    setPreferredOutput("");
                    setDirectRating(0);
                    setAgentRating(0);
                    setRationale("");
                    setAdditionalNotes("");
                  }}
                >
                  Update Feedback
                </Button>
              </CardFooter>
            </Card>
          )}
        </div>
        
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Performance Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="space-y-2">
                {comparison.direct_processing_time_ms && (
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Direct Processing Time</dt>
                    <dd>{comparison.direct_processing_time_ms} ms</dd>
                  </div>
                )}
                
                {comparison.agent_processing_time_ms && (
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Agent Processing Time</dt>
                    <dd>{comparison.agent_processing_time_ms} ms</dd>
                  </div>
                )}
                
                {comparison.direct_processing_time_ms && comparison.agent_processing_time_ms && (
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Difference</dt>
                    <dd className={`${
                      comparison.agent_processing_time_ms > comparison.direct_processing_time_ms
                        ? "text-red-600"
                        : "text-green-600"
                    }`}>
                      {comparison.agent_processing_time_ms > comparison.direct_processing_time_ms
                        ? `Agent is ${comparison.agent_processing_time_ms - comparison.direct_processing_time_ms} ms slower`
                        : `Agent is ${comparison.direct_processing_time_ms - comparison.agent_processing_time_ms} ms faster`
                      }
                    </dd>
                  </div>
                )}
              </dl>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Question Reference</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                This comparison is associated with a specific question.
              </p>
            </CardContent>
            <CardFooter>
              <Link href={`/questions/${comparison.question_id}`} className="w-full">
                <Button variant="outline" className="w-full">
                  View Original Question
                </Button>
              </Link>
            </CardFooter>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}