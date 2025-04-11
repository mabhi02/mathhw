// File: abts-generator/src/app/questions/page.tsx
"use client";

import { useState, useEffect } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { PageHeader } from "@/components/layout/page-header";
import { QuestionCard } from "@/components/question/question-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { Plus } from "lucide-react";
import Link from "next/link";
import { questionsApi, Question } from "@/lib/api";

export default function QuestionsPage() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    domain: "",
    complexity: "",
    questionType: "",
  });
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const loadQuestions = async () => {
      try {
        setLoading(true);
        const params: any = {};
        
        if (filters.domain) params.domain = filters.domain;
        if (filters.complexity) params.complexity = filters.complexity;
        if (filters.questionType) params.question_type = filters.questionType;
        
        if (searchTerm) {
          params.keywords = [searchTerm];
        }
        
        const response = await questionsApi.getQuestions(params);
        setQuestions(response.items || []);
      } catch (error) {
        console.error("Error loading questions:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadQuestions();
  }, [filters, searchTerm]);

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      domain: "",
      complexity: "",
      questionType: "",
    });
    setSearchTerm("");
  };

  return (
    <MainLayout>
      <PageHeader
        title="Question Library"
        description="Browse and manage your generated questions"
        actions={
          <Link href="/generate">
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              <span>New Question</span>
            </Button>
          </Link>
        }
      />

      <div className="mb-8 space-y-4">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[240px]">
            <Input
              placeholder="Search questions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />
          </div>
          
          <div className="w-full sm:w-auto">
            <Select
              value={filters.domain}
              onValueChange={(value) => handleFilterChange("domain", value)}
            >
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="Domain" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Domains</SelectItem>
                <SelectItem value="cardiology">Cardiology</SelectItem>
                <SelectItem value="neurology">Neurology</SelectItem>
                <SelectItem value="surgery">Surgery</SelectItem>
                <SelectItem value="gastroenterology">Gastroenterology</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="w-full sm:w-auto">
            <Select
              value={filters.complexity}
              onValueChange={(value) => handleFilterChange("complexity", value)}
            >
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="Complexity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Complexity</SelectItem>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="w-full sm:w-auto">
            <Select
              value={filters.questionType}
              onValueChange={(value) => handleFilterChange("questionType", value)}
            >
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="Question Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Types</SelectItem>
                <SelectItem value="multiple-choice">Multiple Choice</SelectItem>
                <SelectItem value="true-false">True/False</SelectItem>
                <SelectItem value="short-answer">Short Answer</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <Button 
            variant="outline" 
            onClick={clearFilters}
            className="w-full sm:w-auto"
          >
            Clear Filters
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="text-center p-8">
          <p>Loading questions...</p>
        </div>
      ) : questions.length > 0 ? (
        <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {questions.map((question) => (
            <QuestionCard key={question.id} question={question} />
          ))}
        </div>
      ) : (
        <div className="text-center p-8 border rounded-lg bg-muted/40">
          <p>No questions found. Adjust your filters or create a new question.</p>
          <Link href="/generate" className="mt-4 inline-block">
            <Button>Generate New Questions</Button>
          </Link>
        </div>
      )}
    </MainLayout>
  );
}