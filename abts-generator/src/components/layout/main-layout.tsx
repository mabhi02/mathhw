"use client";

import { Navbar } from "@/components/layout/navbar";
import { Heart } from "lucide-react";
import { useRef, useEffect } from "react";

export function MainLayout({ children }: { children: React.ReactNode }) {
  const rippleRef = useRef<HTMLDivElement>(null);
  
  // Mouse ripple effect
  const addRipple = (e: MouseEvent) => {
    if (!rippleRef.current) return;
    
    const ripple = document.createElement('div');
    const rect = rippleRef.current.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height) * 2;
    
    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.left = `${e.clientX - rect.left - (size/2)}px`;
    ripple.style.top = `${e.clientY - rect.top - (size/2)}px`;
    
    ripple.classList.add('ripple');
    rippleRef.current.appendChild(ripple);
    
    setTimeout(() => {
      if (ripple && ripple.parentNode) {
        ripple.parentNode.removeChild(ripple);
      }
    }, 1500);
  };
  
  useEffect(() => {
    // Add mouse move listener for ripple effect
    const handleMouseMove = (e: MouseEvent) => {
      // Throttle the ripple effect to avoid performance issues
      if (Math.random() > 0.97) { // Only create ripple ~3% of the time
        addRipple(e);
      }
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);
  
  return (
    <div className="flex flex-col min-h-screen medical-bg">
      {/* Ripple background container */}
      <div ref={rippleRef} className="ripple-background"></div>
      
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-6">
        {children}
      </main>
      <footer className="border-t border-border/40 py-4 text-center text-sm text-muted-foreground backdrop-blur-sm bg-background/60">
        <div className="container mx-auto px-4">
          <div className="flex flex-col sm:flex-row items-center justify-between">
            <div className="flex items-center mb-2 sm:mb-0">
              <Heart className="h-4 w-4 text-primary mr-2" />
              <span>ABTS Unified Generator &copy; {new Date().getFullYear()}</span>
            </div>
            <div className="flex gap-6">
              <a href="#" className="hover:text-primary transition-colors duration-200">Help</a>
              <a href="#" className="hover:text-primary transition-colors duration-200">Documentation</a>
              <a href="#" className="hover:text-primary transition-colors duration-200">About</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}