// 1. Navigation Component (src/components/layout/navbar.tsx)
import Link from "next/link";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Menu, X } from "lucide-react";

const navItems = [
  { label: "Outlines", href: "/outlines" },
  { label: "Templates", href: "/templates" },
  { label: "Questions", href: "/questions" },
  { label: "Comparisons", href: "/comparisons" },
];

export function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="bg-background sticky top-0 z-40 border-b">
      <div className="container mx-auto px-4 flex h-16 items-center justify-between">
        <div className="flex items-center">
          <Link href="/" className="font-bold text-xl mr-6">
            ABTS Generator
          </Link>
          <nav className="hidden md:flex items-center space-x-4">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-foreground/70 hover:text-foreground transition"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        
        <div className="hidden md:flex items-center space-x-4">
          <Link href="/generate">
            <Button>Generate Questions</Button>
          </Link>
        </div>
        
        <div className="md:hidden">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </Button>
        </div>
      </div>
      
      {/* Mobile menu */}
      <div
        className={cn(
          "md:hidden absolute w-full bg-background border-b transition-all duration-300 ease-in-out",
          mobileMenuOpen ? "max-h-[300px] py-4" : "max-h-0 overflow-hidden"
        )}
      >
        <div className="container mx-auto px-4 space-y-4">
          <nav className="flex flex-col space-y-4">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-foreground/70 hover:text-foreground transition"
                onClick={() => setMobileMenuOpen(false)}
              >
                {item.label}
              </Link>
            ))}
          </nav>
          <Link href="/generate" onClick={() => setMobileMenuOpen(false)}>
            <Button className="w-full">Generate Questions</Button>
          </Link>
        </div>
      </div>
    </header>
  );
}