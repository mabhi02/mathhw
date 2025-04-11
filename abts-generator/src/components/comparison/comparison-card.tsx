// 5. Comparison Card Component (src/components/comparison/comparison-card.tsx)
import React from "react";
import Link from "next/link";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ComparisonResult } from "@/lib/api";
import { truncateText, formatDate } from "@/lib/utils";
import { ArrowRight } from "lucide-react";

interface ComparisonCardProps {
  comparison: ComparisonResult;
}

export function ComparisonCard({ comparison }: ComparisonCardProps) {
  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="line-clamp-2 text-lg">
          {truncateText(comparison.input_text, 80)}
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Created: {formatDate(comparison.created_at)}
        </p>
      </CardHeader>
      
      <CardContent className="flex-grow">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="text-sm font-medium mb-1">Direct</h4>
            <p className="text-sm text-muted-foreground line-clamp-3">
              {truncateText(comparison.direct_output, 100)}
            </p>
          </div>
          
          <div>
            <h4 className="text-sm font-medium mb-1">Agent</h4>
            <p className="text-sm text-muted-foreground line-clamp-3">
              {truncateText(comparison.agent_output, 100)}
            </p>
          </div>
        </div>
      </CardContent>
      
      <CardFooter>
        <Link href={`/comparisons/${comparison.id}`} className="w-full">
          <Button variant="outline" className="w-full flex items-center justify-between">
            <span>View Comparison</span>
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}