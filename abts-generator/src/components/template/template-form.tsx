// 9. Template Form Component (src/components/template/template-form.tsx)
import { useState } from "react";
import { Template } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

interface TemplateFormProps {
  template: Template;
  onSubmit: (values: Record<string, any>) => void;
  isLoading?: boolean;
}

export function TemplateForm({ template, onSubmit, isLoading = false }: TemplateFormProps) {
  const [formValues, setFormValues] = useState<Record<string, string>>({});
  
  const handleChange = (variable: string, value: string) => {
    setFormValues(prev => ({
      ...prev,
      [variable]: value
    }));
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formValues);
  };
  
  const isRequired = (variable: string) => {
    return template.required_variables && template.required_variables.includes(variable);
  };
  
  // Helper to determine if input should be textarea
  const isLongText = (variable: string) => {
    return variable.includes("explanation") || 
           variable.includes("scenario") || 
           variable.includes("description") ||
           variable.includes("content");
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {template.variables.map((variable) => (
        <div key={variable} className="space-y-2">
          <label className="text-sm font-medium flex items-center">
            {variable.replace(/_/g, " ")}
            {isRequired(variable) && (
              <span className="text-red-500 ml-1">*</span>
            )}
          </label>
          
          {isLongText(variable) ? (
            <Textarea 
              value={formValues[variable] || ""}
              onChange={(e) => handleChange(variable, e.target.value)}
              placeholder={`Enter ${variable.replace(/_/g, " ")}`}
              required={isRequired(variable)}
              rows={4}
            />
          ) : (
            <Input
              value={formValues[variable] || ""}
              onChange={(e) => handleChange(variable, e.target.value)}
              placeholder={`Enter ${variable.replace(/_/g, " ")}`}
              required={isRequired(variable)}
            />
          )}
        </div>
      ))}
      
      <Button 
        type="submit" 
        disabled={isLoading || template.required_variables?.some(v => !formValues[v])}
        className="w-full"
      >
        {isLoading ? "Processing..." : "Preview Template"}
      </Button>
    </form>
  );
}