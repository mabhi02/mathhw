// 6. Question Card Component (src/components/question/question-card.tsx)
import Link from "next/link";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Question } from "@/lib/api";
import { truncateText } from "@/lib/utils";
import { ArrowRight } from "lucide-react";

interface QuestionCardProps {
  question: Question;
}

export function QuestionCard({ question }: QuestionCardProps) {
  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <div className="flex justify-between items-start gap-2">
          <CardTitle className="text-lg line-clamp-2">
            {truncateText(question.text, 80)}
          </CardTitle>
        </div>
        {question.question_type && (
          <div className="flex items-center mt-2">
            <span className="inline-flex items-center rounded-full bg-muted px-2.5 py-0.5 text-xs font-semibold">
              {question.question_type.replace("-", " ")}
            </span>
          </div>
        )}
      </CardHeader>
      
      <CardContent className="flex-grow">
        {question.options && question.options.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium">Options:</p>
            <ul className="list-disc list-inside text-sm space-y-1">
              {question.options.slice(0, 3).map((option) => (
                <li 
                  key={option.id} 
                  className={option.is_correct ? "text-green-600 dark:text-green-400" : ""}
                >
                  {truncateText(option.text, 50)} {option.is_correct && "(Correct)"}
                </li>
              ))}
              {question.options.length > 3 && (
                <li className="list-none text-sm text-muted-foreground italic">
                  + {question.options.length - 3} more options
                </li>
              )}
            </ul>
          </div>
        )}
        
        {question.explanation && (
          <div className="mt-3">
            <p className="text-sm font-medium">Explanation:</p>
            <p className="text-sm text-muted-foreground line-clamp-3">
              {truncateText(question.explanation, 100)}
            </p>
          </div>
        )}
      </CardContent>
      
      <CardFooter className="pt-0">
        <Link href={`/questions/${question.id}`} className="w-full">
          <Button variant="outline" className="w-full flex items-center justify-between">
            <span>View Question</span>
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}