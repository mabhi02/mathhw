// File: src/components/layout/navbar.tsx
import Link from "next/link";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Menu, X, Sun, Moon, Beaker } from "lucide-react";
import { usePathname } from "next/navigation";

const navItems = [
  { label: "Outlines", href: "/outlines" },
  { label: "Templates", href: "/templates" },
  { label: "Questions", href: "/questions" },
  { label: "Comparisons", href: "/comparisons" },
];

interface NavbarProps {
  theme: "light" | "dark";
  toggleTheme: () => void;
}

export function Navbar({ theme, toggleTheme }: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  // Function to check if a link is active
  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname?.startsWith(href);
  };

  return (
    <header className="bg-background sticky top-0 z-40 border-b">
      <div className="container mx-auto px-4 flex h-16 items-center justify-between">
        <div className="flex items-center">
          <Link href="/" className="font-bold text-xl mr-6 flex items-center gap-2">
            <Beaker className="h-5 w-5 text-primary" />
            <span>ABTS Generator</span>
          </Link>
          <nav className="hidden md:flex items-center space-x-4">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "text-sm transition",
                  isActive(item.href) 
                    ? "text-foreground font-medium" 
                    : "text-foreground/70 hover:text-foreground"
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        
        <div className="hidden md:flex items-center space-x-4">
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={toggleTheme}
            className="rounded-full"
            aria-label={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
          >
            {theme === "light" ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </Button>
          
          <Link href="/generate">
            <Button className="flex items-center gap-2">
              <Beaker className="h-4 w-4" />
              <span>Generate Questions</span>
            </Button>
          </Link>
        </div>
        
        <div className="md:hidden flex items-center gap-2">
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={toggleTheme}
            className="rounded-full"
            aria-label={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
          >
            {theme === "light" ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </Button>
          
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
                className={cn(
                  "text-sm transition",
                  isActive(item.href) 
                    ? "text-foreground font-medium" 
                    : "text-foreground/70 hover:text-foreground"
                )}
                onClick={() => setMobileMenuOpen(false)}
              >
                {item.label}
              </Link>
            ))}
          </nav>
          <Link href="/generate" onClick={() => setMobileMenuOpen(false)}>
            <Button className="w-full flex items-center justify-center gap-2">
              <Beaker className="h-4 w-4" />
              <span>Generate Questions</span>
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
}