"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Menu, X, Heart } from "lucide-react";
import { usePathname } from "next/navigation";

const navItems = [
  { label: "Outlines", href: "/outlines" },
  { label: "Templates", href: "/templates" },
  { label: "Questions", href: "/questions" },
  { label: "Comparisons", href: "/comparisons" },
];

export function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [mounted, setMounted] = useState(false);
  const pathname = usePathname();

  // Function to check if a link is active
  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname?.startsWith(href);
  };

  // Listen for scroll events
  useEffect(() => {
    const handleScroll = () => {
      const offset = window.scrollY;
      setScrolled(offset > 10);
    };

    setMounted(true);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={cn(
      "bg-background/80 backdrop-blur-sm sticky top-0 z-40 transition-all duration-300",
      scrolled ? "border-b shadow-sm" : "border-transparent"
    )}>
      <div className="container mx-auto px-4 flex h-16 items-center justify-between">
        <div className="flex items-center">
          <Link href="/" className={cn(
            "abts-logo flex items-center gap-2 group",
            mounted ? "opacity-100" : "opacity-0",
            "transition-opacity duration-300"
          )}>
            <Heart className={cn(
              "h-5 w-5 text-primary transition-transform duration-300",
              "group-hover:text-accent"
            )} />
            <span className="relative">
              ABTS Generator
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary group-hover:w-full transition-all duration-300"></span>
            </span>
          </Link>
          <nav className="hidden md:flex items-center space-x-6 ml-8">
            {navItems.map((item, index) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "nav-item text-sm transition-colors duration-300",
                  isActive(item.href) 
                    ? "text-foreground font-medium" 
                    : "text-foreground/70 hover:text-foreground",
                  mounted ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0",
                  `delay-[${100 + index * 50}ms]`
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        
        <div className="hidden md:flex items-center space-x-4">
          <Link href="/generate">
            <button className={cn(
              "abts-button flex items-center gap-2",
              mounted ? "opacity-100 translate-x-0" : "opacity-0 translate-x-4",
              "transition-all duration-500 delay-300"
            )}>
              Generate Questions
            </button>
          </Link>
        </div>
        
        <div className="md:hidden flex items-center">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
            className="p-2 text-foreground transition-colors duration-200"
          >
            {mobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
        </div>
      </div>
      
      {/* Mobile menu */}
      <div
        className={cn(
          "md:hidden absolute w-full bg-background/95 border-b transition-all duration-300 ease-in-out backdrop-blur-sm",
          mobileMenuOpen ? "max-h-[300px] py-4" : "max-h-0 py-0 overflow-hidden pointer-events-none"
        )}
      >
        <div className="container mx-auto px-4 space-y-4">
          <nav className="flex flex-col space-y-4">
            {navItems.map((item, index) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "text-sm transition-all duration-200",
                  isActive(item.href) 
                    ? "text-foreground font-medium" 
                    : "text-foreground/70 hover:text-foreground",
                  `transition-all delay-[${index * 50}ms]`,
                  mobileMenuOpen ? "translate-x-0 opacity-100" : "translate-x-4 opacity-0"
                )}
                onClick={() => setMobileMenuOpen(false)}
              >
                {item.label}
              </Link>
            ))}
          </nav>
          <Link href="/generate" onClick={() => setMobileMenuOpen(false)}>
            <button className={cn(
              "w-full abts-button flex items-center justify-center gap-2",
              "transition-all duration-300 delay-300",
              mobileMenuOpen ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"
            )}>
              Generate Questions
            </button>
          </Link>
        </div>
      </div>
    </header>
  );
}