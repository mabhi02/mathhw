// 7. Outline Card Component (src/components/outline/outline-card.tsx)
import Link from "next/link";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Outline } from "@/lib/api";
import { ArrowRight, Beaker } from "lucide-react";

interface OutlineCardProps {
  outline: Outline;
}

export function OutlineCard({ outline }: OutlineCardProps) {
  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="line-clamp-2">{outline.title}</CardTitle>
      </CardHeader>
      
      <CardContent className="flex-grow">
        {outline.description ? (
          <p className="text-sm text-muted-foreground line-clamp-3">
            {outline.description}
          </p>
        ) : (
          <p className="text-sm text-muted-foreground italic">
            No description provided
          </p>
        )}
        
        {outline.metadata && (
          <div className="mt-4 flex flex-wrap gap-1">
            {Object.entries(outline.metadata)
              .filter(([key]) => key !== "keywords" && key !== "description")
              .slice(0, 3)
              .map(([key, value]) => (
                <span
                  key={key}
                  className="inline-flex items-center rounded-full bg-muted px-2.5 py-0.5 text-xs font-semibold"
                >
                  {`${key}: ${typeof value === "string" ? value : JSON.stringify(value)}`}
                </span>
              ))}
          </div>
        )}
      </CardContent>
      
      <CardFooter className="grid grid-cols-2 gap-2">
        <Link href={`/outlines/${outline.id}`} className="col-span-1">
          <Button variant="outline" className="w-full flex items-center justify-center gap-1">
            <span>View</span>
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
        <Link href={`/generate?outlineId=${outline.id}`} className="col-span-1">
          <Button variant="default" className="w-full flex items-center justify-center gap-1">
            <span>Generate</span>
            <Beaker className="h-4 w-4" />
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}