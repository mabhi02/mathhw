// File: src/components/layout/main-layout.tsx
"use client";

import { Navbar } from "@/components/layout/navbar";
import { useState, useEffect } from "react";

export function MainLayout({ children }: { children: React.ReactNode }) {
  // Add basic theme detection
  const [theme, setTheme] = useState<"light" | "dark">("light");
  
  useEffect(() => {
    // Check for system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setTheme("dark");
      document.documentElement.classList.add("dark");
    }
    
    // Listen for changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      setTheme(e.matches ? "dark" : "light");
      if (e.matches) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    };
    
    try {
      // Modern API (newer browsers)
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } catch (e) {
      // Fallback for older browsers
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, []);

  // Function to toggle theme
  const toggleTheme = () => {
    if (theme === "light") {
      setTheme("dark");
      document.documentElement.classList.add("dark");
    } else {
      setTheme("light");
      document.documentElement.classList.remove("dark");
    }
  };
  
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar theme={theme} toggleTheme={toggleTheme} />
      <main className="flex-1 container mx-auto px-4 py-6">
        {children}
      </main>
      <footer className="border-t py-4 text-center text-sm text-muted-foreground">
        <div className="container mx-auto px-4">
          <div className="flex flex-col sm:flex-row items-center justify-between">
            <div>
              ABTS Unified Generator &copy; {new Date().getFullYear()}
            </div>
            <div className="flex gap-4 mt-2 sm:mt-0">
              <a href="#" className="hover:underline">Help</a>
              <a href="#" className="hover:underline">Documentation</a>
              <a href="#" className="hover:underline">About</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}