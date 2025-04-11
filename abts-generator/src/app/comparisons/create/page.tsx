// File: abts-generator/src/app/comparisons/create/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { MainLayout } from "@/components/layout/main-layout";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { comparisonsApi, questionsApi, Question } from "@/lib/api";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function ComparisonCreatePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const questionId = searchParams.get("questionId");

  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [loadingQuestions, setLoadingQuestions] = useState(true);
  
  // Form state
  const [selectedQuestionId, setSelectedQuestionId] = useState(questionId || "");
  const [inputText, setInputText] = useState("");
  const [directOutput, setDirectOutput] = useState("");
  const [agentOutput, setAgentOutput] = useState("");
  const [directProcessingTime, setDirectProcessingTime] = useState("");
  const [agentProcessingTime, setAgentProcessingTime] = useState("");
  
  // Processing state
  const [processingDirect, setProcessingDirect] = useState(false);
  const [processingAgent, setProcessingAgent] = useState(false);

  // Effect to load questions
  useEffect(() => {
    const loadQuestions = async () => {
      try {
        setLoadingQuestions(true);
        const response = await questionsApi.getQuestions();
        setQuestions(response.items || []);
      } catch (error) {
        console.error("Error loading questions:", error);
      } finally {
        setLoadingQuestions(false);
      }
    };
    
    loadQuestions();
  }, []);

  // Effect to load selected question
  useEffect(() => {
    const loadSelectedQuestion = async () => {
      if (!selectedQuestionId) return;
      
      try {
        setLoading(true);
        const question = await questionsApi.getQuestion(selectedQuestionId);
        setInputText(question.text);
      } catch (error) {
        console.error("Error loading question:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadSelectedQuestion();
  }, [selectedQuestionId]);

  const handleDirectGenerate = async () => {
    if (!inputText || processingDirect) return;
    
    try {
      setProcessingDirect(true);
      const startTime = performance.now();
      
      // This would normally call a direct GPT-4o generation API
      // Simulating for this demo
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const endTime = performance.now();
      setDirectProcessingTime((endTime - startTime).toFixed(0));
      
      setDirectOutput("This is a simulated direct GPT-4o response. In a real implementation, this would call the API to generate a response directly from the model without using an agent pipeline.");
    } catch (error) {
      console.error("Error generating direct output:", error);
      alert("Error generating direct output. Please try again.");
    } finally {
      setProcessingDirect(false);
    }
  };

  const handleAgentGenerate = async () => {
    if (!inputText || processingAgent) return;
    
    try {
      setProcessingAgent(true);
      const startTime = performance.now();
      
      // This would normally call the agent pipeline
      // Simulating for this demo
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const endTime = performance.now();
      setAgentProcessingTime((endTime - startTime).toFixed(0));
      
      setAgentOutput("This is a simulated agent pipeline response. In a real implementation, this would process the input through multiple specialized agents to generate a more sophisticated output. The agent pipeline typically takes longer but may produce better results for complex tasks.");
    } catch (error) {
      console.error("Error generating agent output:", error);
      alert("Error generating agent output. Please try again.");
    } finally {
      setProcessingAgent(false);
    }
  };

  const handleSubmit = async () => {
    if (!selectedQuestionId || !inputText || !directOutput || !agentOutput || submitting) {
      return;
    }
    
    try {
      setSubmitting(true);
      
      const comparisonData = {
        question_id: selectedQuestionId,
        input_text: inputText,
        direct_output: directOutput,
        agent_output: agentOutput,
        direct_processing_time_ms: directProcessingTime ? parseInt(directProcessingTime) : undefined,
        agent_processing_time_ms: agentProcessingTime ? parseInt(agentProcessingTime) : undefined
      };
      
      const result = await comparisonsApi.createComparison(comparisonData);
      router.push(`/comparisons/${result.id}`);
    } catch (error) {
      console.error("Error creating comparison:", error);
      alert("Error creating comparison. Please try again.");
      setSubmitting(false);
    }
  };

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
        title="Create Comparison"
        description="Compare direct GPT-4o and agent-based generation side by side"
      />

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Input Settings</CardTitle>
            <CardDescription>
              Select a question or enter custom input text to compare
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Select Question (Optional)
                </label>
                <Select
                  value={selectedQuestionId}
                  onValueChange={setSelectedQuestionId}
                  disabled={loadingQuestions}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a question" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">No question (custom input)</SelectItem>
                    {questions.map((question) => (
                      <SelectItem key={question.id} value={question.id}>
                        {question.text.substring(0, 60)}...
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">
                  Input Text
                </label>
                <Textarea
                  placeholder="Enter input text for the comparison..."
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  rows={5}
                  disabled={loading}
                />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Direct GPT-4o Generation</CardTitle>
              <CardDescription>
                Generate output directly from GPT-4o
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder="Direct output will appear here..."
                value={directOutput}
                onChange={(e) => setDirectOutput(e.target.value)}
                rows={10}
                className="mb-2"
              />
              {directProcessingTime && (
                <p className="text-sm text-muted-foreground">
                  Processing time: {directProcessingTime} ms
                </p>
              )}
            </CardContent>
            <CardFooter>
              <Button 
                onClick={handleDirectGenerate} 
                disabled={!inputText || processingDirect}
                className="w-full"
              >
                {processingDirect ? "Generating..." : "Generate Direct Output"}
              </Button>
            </CardFooter>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Agent Pipeline Generation</CardTitle>
              <CardDescription>
                Generate output using the agent pipeline
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder="Agent output will appear here..."
                value={agentOutput}
                onChange={(e) => setAgentOutput(e.target.value)}
                rows={10}
                className="mb-2"
              />
              {agentProcessingTime && (
                <p className="text-sm text-muted-foreground">
                  Processing time: {agentProcessingTime} ms
                </p>
              )}
            </CardContent>
            <CardFooter>
              <Button 
                onClick={handleAgentGenerate} 
                disabled={!inputText || processingAgent}
                className="w-full"
              >
                {processingAgent ? "Generating..." : "Generate Agent Output"}
              </Button>
            </CardFooter>
          </Card>
        </div>
        
        <div className="flex justify-end">
          <Button 
            onClick={handleSubmit} 
            disabled={!selectedQuestionId || !inputText || !directOutput || !agentOutput || submitting}
            size="lg"
          >
            {submitting ? "Creating..." : "Create Comparison"}
          </Button>
        </div>
      </div>
    </MainLayout>
  );
}