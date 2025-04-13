"use client";

import { useState } from "react";
import Link from "next/link";
import { Beaker, Book, FileText, Loader2, ArrowRight } from "lucide-react";

export default function GeneratePage() {
  const [contentInput, setContentInput] = useState("");
  const [questionType, setQuestionType] = useState("multiple-choice");
  const [complexity, setComplexity] = useState("medium");
  const [count, setCount] = useState(3);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState<any[]>([]);

  const handleGenerate = async () => {
    if (!contentInput) return;
    
    try {
      setIsGenerating(true);
      
      // Simulate API call with a delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Sample questions for demo
      const sampleQuestions = [
        {
          id: "q1",
          text: "Which of the following is a complication of atrial fibrillation?",
          explanation: "Atrial fibrillation increases the risk of thromboembolic events, particularly stroke, due to blood stasis in the left atrial appendage.",
          options: [
            { id: "o1", text: "Stroke", is_correct: true },
            { id: "o2", text: "Pulmonary hypertension", is_correct: false },
            { id: "o3", text: "Aortic stenosis", is_correct: false },
            { id: "o4", text: "Pneumothorax", is_correct: false }
          ],
          domain: "cardiology",
          question_type: questionType,
          cognitive_complexity: complexity
        },
        {
          id: "q2",
          text: "A 65-year-old patient with atrial fibrillation has a CHA₂DS₂-VASc score of 4. What is the most appropriate anticoagulation strategy?",
          explanation: "For patients with atrial fibrillation and a CHA₂DS₂-VASc score of 2 or greater in men or 3 or greater in women, oral anticoagulation is recommended. DOACs are generally preferred over warfarin unless there are specific contraindications.",
          options: [
            { id: "o1", text: "No anticoagulation required", is_correct: false },
            { id: "o2", text: "Aspirin only", is_correct: false },
            { id: "o3", text: "Direct oral anticoagulant (DOAC)", is_correct: true },
            { id: "o4", text: "Dual antiplatelet therapy", is_correct: false }
          ],
          domain: "cardiology",
          question_type: questionType,
          cognitive_complexity: complexity
        },
        {
          id: "q3",
          text: "What ECG finding is pathognomonic for atrial fibrillation?",
          explanation: "Atrial fibrillation is characterized by the absence of P waves and an irregularly irregular ventricular rhythm on ECG. The absence of organized atrial activity results in fibrillatory waves (f waves) which are irregular in timing and morphology.",
          options: [
            { id: "o1", text: "ST-segment elevation", is_correct: false },
            { id: "o2", text: "Irregularly irregular rhythm with absence of P waves", is_correct: true },
            { id: "o3", text: "Prolonged PR interval", is_correct: false },
            { id: "o4", text: "Widened QRS complex", is_correct: false }
          ],
          domain: "cardiology",
          question_type: questionType,
          cognitive_complexity: complexity
        }
      ];
      
      // Update state with generated questions
      setGeneratedQuestions(sampleQuestions.slice(0, count));
    } catch (error) {
      console.error("Error generating questions:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b py-4 bg-background">
        <div className="container">
          <div className="flex justify-between items-center">
            <Link href="/" className="font-bold text-xl flex items-center gap-2 text-primary">
              <Beaker className="h-5 w-5" />
              <span>ABTS Generator</span>
            </Link>
            <nav className="hidden md:flex space-x-6">
              <Link href="/outlines" className="text-foreground/70 hover:text-primary transition">Outlines</Link>
              <Link href="/templates" className="text-foreground/70 hover:text-primary transition">Templates</Link>
              <Link href="/questions" className="text-foreground/70 hover:text-primary transition">Questions</Link>
              <Link href="/comparisons" className="text-foreground/70 hover:text-primary transition">Comparisons</Link>
              <Link href="/generate" className="bg-primary text-primary-foreground py-2 px-4 rounded-md hover:bg-primary/90 transition">
                Generate
              </Link>
            </nav>
            <button className="md:hidden text-foreground">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 py-8">
        <div className="container">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold">Generate Questions</h1>
            <div className="flex space-x-2">
              <Link href="/outlines" className="inline-flex items-center justify-center rounded-md text-sm font-medium border bg-background hover:bg-muted transition-colors h-10 px-4 py-2">
                <Book className="mr-2 h-4 w-4" />
                <span>Outlines</span>
              </Link>
              <Link href="/templates" className="inline-flex items-center justify-center rounded-md text-sm font-medium border bg-background hover:bg-muted transition-colors h-10 px-4 py-2">
                <FileText className="mr-2 h-4 w-4" />
                <span>Templates</span>
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Input panel */}
            <div className="lg:col-span-1">
              <div className="bg-card border rounded-lg shadow-sm h-full">
                <div className="p-6">
                  <h2 className="text-xl font-semibold mb-4">Input</h2>
                  <div className="space-y-4">
                    <div>
                      <label htmlFor="content" className="block text-sm font-medium mb-1">Question Content</label>
                      <textarea
                        id="content"
                        className="w-full p-3 border rounded-md bg-background"
                        rows={6}
                        placeholder="Enter medical content to generate questions..."
                        value={contentInput}
                        onChange={(e) => setContentInput(e.target.value)}
                      ></textarea>
                    </div>

                    <div>
                      <label htmlFor="questionType" className="block text-sm font-medium mb-1">Question Type</label>
                      <select
                        id="questionType"
                        className="w-full p-2 border rounded-md bg-background"
                        value={questionType}
                        onChange={(e) => setQuestionType(e.target.value)}
                      >
                        <option value="multiple-choice">Multiple Choice</option>
                        <option value="true-false">True/False</option>
                        <option value="short-answer">Short Answer</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="complexity" className="block text-sm font-medium mb-1">Complexity</label>
                      <select
                        id="complexity"
                        className="w-full p-2 border rounded-md bg-background"
                        value={complexity}
                        onChange={(e) => setComplexity(e.target.value)}
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="count" className="block text-sm font-medium mb-1">Number of Questions</label>
                      <select
                        id="count"
                        className="w-full p-2 border rounded-md bg-background"
                        value={count}
                        onChange={(e) => setCount(parseInt(e.target.value))}
                      >
                        <option value="1">1</option>
                        <option value="3">3</option>
                        <option value="5">5</option>
                        <option value="10">10</option>
                      </select>
                    </div>

                    <button
                      className={`w-full py-2 px-4 rounded-md inline-flex items-center justify-center ${
                        isGenerating || !contentInput
                          ? "bg-primary/50 cursor-not-allowed"
                          : "bg-primary hover:bg-primary/90"
                      } text-primary-foreground transition-colors`}
                      onClick={handleGenerate}
                      disabled={isGenerating || !contentInput}
                    >
                      {isGenerating ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          <span>Generating...</span>
                        </>
                      ) : (
                        <>
                          <Beaker className="mr-2 h-4 w-4" />
                          <span>Generate Questions</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Results panel */}
            <div className="lg:col-span-2">
              <div className="bg-card border rounded-lg shadow-sm">
                <div className="p-6">
                  <h2 className="text-xl font-semibold mb-4">Generated Questions</h2>

                  {isGenerating ? (
                    <div className="flex items-center justify-center h-64">
                      <div className="text-center">
                        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2 text-primary" />
                        <p className="text-muted-foreground">Generating questions...</p>
                      </div>
                    </div>
                  ) : generatedQuestions.length > 0 ? (
                    <div className="space-y-6">
                      {generatedQuestions.map((question) => (
                        <div key={question.id} className="border rounded-lg p-4">
                          <h3 className="font-semibold text-lg mb-4">{question.text}</h3>
                          
                          {question.options && question.options.length > 0 && (
                            <div className="space-y-2 mb-4">
                              {question.options.map((option: any) => (
                                <div 
                                  key={option.id} 
                                  className={`flex items-start p-3 rounded-md ${
                                    option.is_correct 
                                      ? "bg-green-50 border-green-200 border dark:bg-green-950/20 dark:border-green-900" 
                                      : "bg-muted/40 border"
                                  }`}
                                >
                                  <div className={`w-5 h-5 rounded-full flex items-center justify-center mr-3 mt-0.5 ${
                                    option.is_correct 
                                      ? "bg-green-500 text-white" 
                                      : "border border-muted-foreground"
                                  }`}>
                                    {option.is_correct && "✓"}
                                  </div>
                                  <span>{option.text}</span>
                                </div>
                              ))}
                            </div>
                          )}
                          
                          {question.explanation && (
                            <div className="mt-4 pt-3 border-t">
                              <h4 className="font-medium mb-1">Explanation:</h4>
                              <p className="text-muted-foreground">{question.explanation}</p>
                            </div>
                          )}
                          
                          <div className="mt-4 flex flex-wrap gap-2">
                            {question.domain && (
                              <span className="inline-flex items-center rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-semibold text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">
                                {question.domain}
                              </span>
                            )}
                            {question.question_type && (
                              <span className="inline-flex items-center rounded-full bg-purple-50 px-2.5 py-0.5 text-xs font-semibold text-purple-700 dark:bg-purple-950/50 dark:text-purple-300">
                                {question.question_type.replace("-", " ")}
                              </span>
                            )}
                            {question.cognitive_complexity && (
                              <span className="inline-flex items-center rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-700 dark:bg-amber-950/50 dark:text-amber-300">
                                {question.cognitive_complexity} complexity
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                      
                      <div className="flex justify-end mt-6 space-x-3">
                        <button className="border bg-background hover:bg-muted py-2 px-4 rounded-md inline-flex items-center transition-colors">
                          Regenerate
                        </button>
                        <button className="bg-primary text-primary-foreground hover:bg-primary/90 py-2 px-4 rounded-md inline-flex items-center transition-colors">
                          Save Questions
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="border rounded-lg p-8 text-center h-64 flex items-center justify-center">
                      <div>
                        <p className="text-muted-foreground mb-2">No questions generated yet</p>
                        <p className="text-sm text-muted-foreground">Enter medical content and click "Generate Questions" to create assessment questions</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="py-8 border-t mt-auto">
        <div className="container">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-muted-foreground mb-4 md:mb-0">
              ABTS Unified Generator &copy; {new Date().getFullYear()}
            </div>
            <div className="flex space-x-6">
              <a href="#" className="text-muted-foreground hover:text-foreground transition">About</a>
              <a href="#" className="text-muted-foreground hover:text-foreground transition">Documentation</a>
              <a href="#" className="text-muted-foreground hover:text-foreground transition">GitHub</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}