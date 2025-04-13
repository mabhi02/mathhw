"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Beaker, Book, FileText, Loader2, ArrowRight, Brain, Award, Dices, ChevronDown, Check, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

export default function GeneratePage() {
  const [contentInput, setContentInput] = useState("");
  const [questionType, setQuestionType] = useState("multiple-choice");
  const [complexity, setComplexity] = useState("medium");
  const [count, setCount] = useState(3);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState<any[]>([]);
  const [mounted, setMounted] = useState(false);
  const [activeQuestion, setActiveQuestion] = useState<number | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleGenerate = async () => {
    if (!contentInput) return;
    
    try {
      setIsGenerating(true);
      
      // Simulate progress and delay for visual effect
      await new Promise(resolve => setTimeout(resolve, 2500));
      
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

  const toggleQuestion = (index: number) => {
    if (activeQuestion === index) {
      setActiveQuestion(null);
    } else {
      setActiveQuestion(index);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b py-4 bg-background/80 backdrop-blur-sm sticky top-0 z-10 transition-all duration-300">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center">
            <Link href="/" className="font-bold text-xl flex items-center gap-2 text-primary group">
              <Beaker className="h-5 w-5 transition-transform duration-300 group-hover:rotate-12" />
              <span className="relative">
                ABTS Generator
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary group-hover:w-full transition-all duration-300"></span>
              </span>
            </Link>
            <nav className="hidden md:flex space-x-6">
              {["Outlines", "Templates", "Questions", "Comparisons"].map((item) => (
                <Link key={item} href={`/${item.toLowerCase()}`} className="nav-item text-foreground/70 hover:text-primary transition">
                  {item}
                </Link>
              ))}
              <Link href="/generate" className="bg-primary text-primary-foreground py-2 px-4 rounded-md hover:bg-primary/90 transition relative overflow-hidden group">
                <span className="relative z-10">Generate</span>
                <span className="absolute inset-0 bg-white/20 transform -translate-x-full group-hover:translate-x-0 transition-transform duration-300"></span>
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

      <main className="flex-1 py-8 relative">
        {/* Background pattern */}
        <div className="absolute inset-0 bg-pattern"></div>
        
        <div className="relative z-10 container mx-auto px-4">
          <div className={`flex items-center justify-between mb-8 ${mounted ? 'animate-fadeIn' : 'opacity-0'}`}>
            <h1 className="text-3xl font-bold">Generate Questions</h1>
            <div className="flex space-x-2">
              <Link href="/outlines" className="inline-flex items-center justify-center rounded-md text-sm font-medium border bg-background hover:bg-muted transition-colors h-10 px-4 py-2 group">
                <Book className="mr-2 h-4 w-4 group-hover:scale-110 transition-transform" />
                <span>Outlines</span>
              </Link>
              <Link href="/templates" className="inline-flex items-center justify-center rounded-md text-sm font-medium border bg-background hover:bg-muted transition-colors h-10 px-4 py-2 group">
                <FileText className="mr-2 h-4 w-4 group-hover:scale-110 transition-transform" />
                <span>Templates</span>
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Input panel */}
            <div className={`lg:col-span-1 ${mounted ? 'animate-slideInRight stagger-1' : 'opacity-0'}`}>
              <div className="bg-card border rounded-lg shadow-sm h-full hover-card">
                <div className="p-6">
                  <h2 className="text-xl font-semibold mb-4 flex items-center">
                    <Brain className="h-5 w-5 mr-2 text-primary" />
                    Input
                  </h2>
                  <div className="space-y-4">
                    <div className="transition-all duration-300 ease-in-out">
                      <label htmlFor="content" className="block text-sm font-medium mb-1">Question Content</label>
                      <textarea
                        id="content"
                        className="w-full p-3 border rounded-md bg-background transition-all duration-200 focus:ring-2 focus:ring-primary/50 focus:border-primary"
                        rows={6}
                        placeholder="Enter medical content to generate questions..."
                        value={contentInput}
                        onChange={(e) => setContentInput(e.target.value)}
                      ></textarea>
                    </div>

                    <div className="transition-all duration-300 ease-in-out">
                      <label htmlFor="questionType" className="block text-sm font-medium mb-1">Question Type</label>
                      <div className="relative">
                        <select
                          id="questionType"
                          className="w-full p-2 border rounded-md bg-background appearance-none transition-all duration-200 focus:ring-2 focus:ring-primary/50 focus:border-primary pr-10"
                          value={questionType}
                          onChange={(e) => setQuestionType(e.target.value)}
                        >
                          <option value="multiple-choice">Multiple Choice</option>
                          <option value="true-false">True/False</option>
                          <option value="short-answer">Short Answer</option>
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 pointer-events-none text-muted-foreground" />
                      </div>
                    </div>

                    <div className="transition-all duration-300 ease-in-out">
                      <label htmlFor="complexity" className="block text-sm font-medium mb-1">Complexity</label>
                      <div className="relative">
                        <select
                          id="complexity"
                          className="w-full p-2 border rounded-md bg-background appearance-none transition-all duration-200 focus:ring-2 focus:ring-primary/50 focus:border-primary pr-10"
                          value={complexity}
                          onChange={(e) => setComplexity(e.target.value)}
                        >
                          <option value="low">Low</option>
                          <option value="medium">Medium</option>
                          <option value="high">High</option>
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 pointer-events-none text-muted-foreground" />
                      </div>
                    </div>

                    <div className="transition-all duration-300 ease-in-out">
                      <label htmlFor="count" className="block text-sm font-medium mb-1">Number of Questions</label>
                      <div className="relative">
                        <select
                          id="count"
                          className="w-full p-2 border rounded-md bg-background appearance-none transition-all duration-200 focus:ring-2 focus:ring-primary/50 focus:border-primary pr-10"
                          value={count}
                          onChange={(e) => setCount(parseInt(e.target.value))}
                        >
                          <option value="1">1</option>
                          <option value="3">3</option>
                          <option value="5">5</option>
                          <option value="10">10</option>
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 pointer-events-none text-muted-foreground" />
                      </div>
                    </div>

                    <button
                      className={`w-full py-2 px-4 rounded-md inline-flex items-center justify-center transition-all duration-300 ${
                        isGenerating || !contentInput
                          ? "bg-primary/50 cursor-not-allowed"
                          : "bg-primary hover:bg-primary/90 btn-pulse"
                      } text-primary-foreground relative overflow-hidden group`}
                      onClick={handleGenerate}
                      disabled={isGenerating || !contentInput}
                    >
                      <span className="relative z-10 flex items-center">
                        {isGenerating ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            <span>Generating...</span>
                          </>
                        ) : (
                          <>
                            <Beaker className="mr-2 h-4 w-4 group-hover:rotate-12 transition-transform" />
                            <span>Generate Questions</span>
                          </>
                        )}
                      </span>
                      <span className="absolute inset-0 bg-white/20 transform -translate-x-full group-hover:translate-x-0 transition-transform duration-300"></span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Results panel */}
            <div className={`lg:col-span-2 ${mounted ? 'animate-slideInRight stagger-2' : 'opacity-0'}`}>
              <div className="bg-card border rounded-lg shadow-sm hover-card">
                <div className="p-6">
                  <h2 className="text-xl font-semibold mb-4 flex items-center">
                    <Dices className="h-5 w-5 mr-2 text-primary" />
                    Generated Questions
                  </h2>

                  {isGenerating ? (
                    <div className="flex items-center justify-center h-64 bg-muted/30 rounded-lg border border-dashed">
                      <div className="text-center space-y-3">
                        <div className="relative w-12 h-12 mx-auto">
                          <div className="absolute inset-0 rounded-full border-t-2 border-primary animate-spin"></div>
                          <div className="absolute inset-3 rounded-full bg-primary/20 animate-pulse"></div>
                          <Beaker className="absolute inset-3 h-6 w-6 text-primary animate-bounce" />
                        </div>
                        <p className="text-muted-foreground">Generating questions...</p>
                        <p className="text-xs text-muted-foreground/70">Using AI to create high-quality assessment content</p>
                      </div>
                    </div>
                  ) : generatedQuestions.length > 0 ? (
                    <div className="space-y-6">
                      {generatedQuestions.map((question, index) => (
                        <div 
                          key={question.id} 
                          className={`border rounded-lg transition-all duration-300 overflow-hidden ${
                            activeQuestion === index ? 'shadow-md' : 'hover:shadow-sm'
                          }`}
                        >
                          <div 
                            className={`p-4 cursor-pointer flex items-start justify-between transition-colors duration-200 ${
                              activeQuestion === index ? 'bg-muted/50' : ''
                            }`}
                            onClick={() => toggleQuestion(index)}
                          >
                            <div>
                              <h3 className="font-semibold text-lg">
                                <span className="text-primary mr-2">Q{index+1}.</span> 
                                {question.text}
                              </h3>
                            </div>
                            <div className="flex-shrink-0 ml-2">
                              <ChevronDown className={`h-5 w-5 text-muted-foreground transition-transform duration-300 ${
                                activeQuestion === index ? 'rotate-180' : ''
                              }`} />
                            </div>
                          </div>
                          
                          <div className={cn(
                            "transition-all duration-300 ease-in-out overflow-hidden",
                            activeQuestion === index ? "max-h-[1000px] opacity-100" : "max-h-0 opacity-0"
                          )}>
                            <div className="p-4 pt-2 border-t">
                              {question.options && question.options.length > 0 && (
                                <div className="space-y-2 mb-4">
                                  {question.options.map((option: any) => (
                                    <div 
                                      key={option.id} 
                                      className={`flex items-start p-3 rounded-md transition-all duration-200 ${
                                        option.is_correct 
                                          ? "bg-green-50 border-green-200 border dark:bg-green-950/20 dark:border-green-900" 
                                          : "bg-muted/40 border hover:bg-muted/60"
                                      }`}
                                    >
                                      <div className={`w-5 h-5 rounded-full flex items-center justify-center mr-3 mt-0.5 ${
                                        option.is_correct 
                                          ? "bg-green-500 text-white" 
                                          : "border border-muted-foreground"
                                      }`}>
                                        {option.is_correct && <Check className="h-3 w-3" />}
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
                          </div>
                        </div>
                      ))}
                      
                      <div className="flex justify-end mt-6 space-x-3">
                        <button 
                          className="border bg-background hover:bg-muted py-2 px-4 rounded-md inline-flex items-center transition-colors group"
                          onClick={handleGenerate}
                        >
                          <RefreshCw className="mr-2 h-4 w-4 group-hover:rotate-180 transition-transform duration-500" />
                          Regenerate
                        </button>
                        <button className="bg-primary text-primary-foreground hover:bg-primary/90 py-2 px-4 rounded-md inline-flex items-center transition-colors relative overflow-hidden group">
                          <span className="relative z-10">Save Questions</span>
                          <span className="absolute inset-0 bg-white/20 transform -translate-x-full group-hover:translate-x-0 transition-transform duration-300"></span>
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="border rounded-lg p-8 text-center h-64 flex items-center justify-center bg-muted/30 border-dashed">
                      <div className="space-y-2">
                        <Beaker className="h-10 w-10 mx-auto text-muted-foreground/50" />
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
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-muted-foreground mb-4 md:mb-0">
              ABTS Unified Generator &copy; {new Date().getFullYear()}
            </div>
            <div className="flex space-x-6">
              {["About", "Documentation", "GitHub"].map(link => (
                <a key={link} href="#" className="text-muted-foreground hover:text-foreground transition animated-link">
                  {link}
                </a>
              ))}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}