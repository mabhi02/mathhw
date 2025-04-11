// 8. Outline Node View Component (src/components/outline/outline-node-view.tsx)
import { useState } from "react";
import { OutlineNode } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ChevronRight, ChevronDown, Beaker } from "lucide-react";

interface OutlineNodeViewProps {
  node: OutlineNode;
  onGenerateQuestion?: (node: OutlineNode) => void;
  depth?: number;
}

export function OutlineNodeView({ 
  node, 
  onGenerateQuestion,
  depth = 0 
}: OutlineNodeViewProps) {
  const [expanded, setExpanded] = useState(true);
  const hasChildren = node.children && node.children.length > 0;
  
  const toggleExpand = () => {
    setExpanded(!expanded);
  };
  
  const handleGenerateClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onGenerateQuestion) {
      onGenerateQuestion(node);
    }
  };
  
  return (
    <div className="outline-node">
      <div 
        className={`flex items-start gap-2 ${hasChildren ? 'cursor-pointer' : ''} py-1`}
        onClick={hasChildren ? toggleExpand : undefined}
      >
        {hasChildren && (
          <div className="mt-1">
            {expanded ? (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            )}
          </div>
        )}
        
        <div className="flex-1">
          <div className="flex items-start justify-between gap-2">
            <div>
              <span className="font-medium">{node.title}</span>
              {node.type && (
                <span className="ml-2 text-xs text-muted-foreground">
                  ({node.type})
                </span>
              )}
            </div>
            
            {onGenerateQuestion && (
              <Button 
                variant="outline" 
                size="sm" 
                className="flex items-center gap-1 h-7 text-xs"
                onClick={handleGenerateClick}
              >
                <Beaker className="h-3 w-3" />
                <span>Generate</span>
              </Button>
            )}
          </div>
          
          {node.content && (
            <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
              {node.content}
            </p>
          )}
        </div>
      </div>
      
      {hasChildren && expanded && (
        <div 
          className="ml-4 pl-4 border-l"
          style={{ marginLeft: `${depth > 0 ? 1 : 0.5}rem` }}
        >
          {node.children.map((child) => (
            <OutlineNodeView 
              key={child.id} 
              node={child} 
              onGenerateQuestion={onGenerateQuestion}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}