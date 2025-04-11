// 10. Template Card Component (src/components/template/template-card.tsx)
import Link from "next/link";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Template } from "@/lib/api";
import { ArrowRight, Beaker } from "lucide-react";

interface TemplateCardProps {
  template: Template;
}

export function TemplateCard({ template }: TemplateCardProps) {
  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="line-clamp-2 text-lg">{template.id}</CardTitle>
        <p className="text-sm text-muted-foreground">
          Type: {template.type}
        </p>
      </CardHeader>
      
      <CardContent className="flex-grow">
        {template.description ? (
          <p className="text-sm text-muted-foreground mb-4">
            {template.description}
          </p>
        ) : (
          <p className="text-sm text-muted-foreground mb-4 italic">
            No description provided
          </p>
        )}
        
        <div className="space-y-2">
          <div>
            <h4 className="text-sm font-medium">Variables:</h4>
            <div className="flex flex-wrap gap-1 mt-1">
              {template.variables.slice(0, 5).map((variable) => (
                <span
                  key={variable}
                  className="inline-flex items-center rounded-full bg-muted px-2.5 py-0.5 text-xs font-semibold"
                >
                  {variable}
                </span>
              ))}
              {template.variables.length > 5 && (
                <span className="inline-flex items-center rounded-full bg-muted px-2.5 py-0.5 text-xs font-semibold">
                  +{template.variables.length - 5} more
                </span>
              )}
            </div>
          </div>
          
          {template.has_conditionals && (
            <p className="text-xs text-amber-600">
              Contains conditional logic
            </p>
          )}
        </div>
      </CardContent>
      
      <CardFooter className="grid grid-cols-2 gap-2">
        <Link href={`/templates/${template.id}`} className="col-span-1">
          <Button variant="outline" className="w-full flex items-center justify-center gap-1">
            <span>View</span>
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
        <Link href={`/generate?templateId=${template.id}`} className="col-span-1">
          <Button variant="default" className="w-full flex items-center justify-center gap-1">
            <span>Use</span>
            <Beaker className="h-4 w-4" />
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}