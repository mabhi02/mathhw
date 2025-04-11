// File: abts-generator/src/app/comparisons/page.tsx
"use client";

import { useState, useEffect } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { PageHeader } from "@/components/layout/page-header";
import { ComparisonCard } from "@/components/comparison/comparison-card";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import Link from "next/link";
import { comparisonsApi, ComparisonResult } from "@/lib/api";

export default function ComparisonsPage() {
  const [comparisons, setComparisons] = useState<ComparisonResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadComparisons = async () => {
      try {
        setLoading(true);
        const data = await comparisonsApi.getComparisons();
        setComparisons(data);
      } catch (error) {
        console.error("Error loading comparisons:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadComparisons();
  }, []);

  return (
    <MainLayout>
      <PageHeader
        title="A/B Comparisons"
        description="Compare direct GPT-4o outputs with agent-based generation"
        actions={
          <Link href="/comparisons/create">
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              <span>New Comparison</span>
            </Button>
          </Link>
        }
      />

      {loading ? (
        <div className="text-center p-8">
          <p>Loading comparisons...</p>
        </div>
      ) : comparisons.length > 0 ? (
        <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {comparisons.map((comparison) => (
            <ComparisonCard key={comparison.id} comparison={comparison} />
          ))}
        </div>
      ) : (
        <div className="text-center p-8 border rounded-lg bg-muted/40">
          <p>No comparisons found. Create a new comparison to get started.</p>
          <Link href="/comparisons/create" className="mt-4 inline-block">
            <Button>Create New Comparison</Button>
          </Link>
        </div>
      )}
    </MainLayout>
  );
}