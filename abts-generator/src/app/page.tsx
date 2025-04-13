"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { Heart, Stethoscope, Clipboard, FileText, BarChart, Play } from "lucide-react";

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const rippleRef = useRef<HTMLDivElement>(null);
  
  // Mouse ripple effect
  const addRipple = (e: React.MouseEvent<HTMLDivElement> | MouseEvent) => {
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
    setMounted(true);
    
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
    <div className="min-h-screen flex flex-col medical-bg">
      {/* Ripple background container */}
      <div ref={rippleRef} className="ripple-background"></div>
      
      <header className="border-b border-border/40 py-4 backdrop-blur-sm bg-background/80 sticky top-0 z-10">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center">
            <Link href="/" className="abts-logo flex items-center gap-2 group">
              <Heart className="h-5 w-5 text-primary group-hover:text-accent transition-colors duration-300" />
              <span className="relative">
                ABTS Generator
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary group-hover:w-full transition-all duration-300"></span>
              </span>
            </Link>
            <nav className="hidden md:flex space-x-8">
              {[
                { name: "Outlines", href: "/outlines" },
                { name: "Templates", href: "/templates" },
                { name: "Questions", href: "/questions" },
                { name: "Comparisons", href: "/comparisons" }
              ].map((item) => (
                <Link 
                  key={item.name} 
                  href={item.href} 
                  className="nav-item text-foreground/80 hover:text-primary transition-colors duration-300"
                >
                  {item.name}
                </Link>
              ))}
              <Link 
                href="/generate" 
                className="abts-button flex items-center gap-2"
              >
                Generate
              </Link>
            </nav>
            <button className="md:hidden text-foreground">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <div className="container mx-auto px-4 py-12">
          <div className="text-center mb-16">
            <h1 className={`text-5xl font-bold mb-6 transition-all duration-700 ${mounted ? 'opacity-100' : 'opacity-0 transform translate-y-4'}`}>
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent">
                ABTS Unified Generator
              </span>
            </h1>
            <p className={`text-xl text-foreground/80 max-w-2xl mx-auto transition-all duration-700 delay-300 ${mounted ? 'opacity-100' : 'opacity-0 transform translate-y-4'}`}>
              Streamline the creation of high-quality thoracic surgery assessment questions with AI-powered generation tools.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {[
              {
                title: "Content Outlines",
                description: "Manage structured content outlines for organized thoracic surgery question generation",
                icon: <Clipboard className="h-6 w-6 text-primary" />,
                link: "/outlines",
                linkText: "Explore Outlines",
                delay: 100
              },
              {
                title: "Question Templates",
                description: "Standardize your question formats with customizable thoracic surgery templates",
                icon: <FileText className="h-6 w-6 text-primary" />,
                link: "/templates",
                linkText: "Browse Templates",
                delay: 200
              },
              {
                title: "Question Generation",
                description: "Generate high-quality thoracic surgery questions using AI",
                icon: <Stethoscope className="h-6 w-6 text-primary" />,
                link: "/generate",
                linkText: "Generate Questions",
                delay: 300
              },
              {
                title: "Question Library",
                description: "Browse, filter, and manage your generated thoracic surgery questions",
                icon: <BarChart className="h-6 w-6 text-primary" />,
                link: "/questions",
                linkText: "View Questions",
                delay: 400
              },
              {
                title: "A/B Comparisons",
                description: "Compare direct vs. agent-based question generation approaches",
                icon: <Heart className="h-6 w-6 text-primary" />,
                link: "/comparisons",
                linkText: "View Comparisons",
                delay: 500
              },
              {
                title: "Get Started",
                description: "Begin generating thoracic surgery questions with our AI-powered tools",
                icon: <Play className="h-6 w-6 text-white" />,
                link: "/generate",
                linkText: "Start Now",
                isHighlighted: true,
                delay: 600
              }
            ].map((feature, index) => (
              <div 
                key={feature.title}
                className={`abts-card transition-all duration-500 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}
                style={{ transitionDelay: `${feature.delay}ms` }}
              >
                <div className={`p-6 h-full flex flex-col ${feature.isHighlighted ? 'bg-primary text-white' : ''}`}>
                  <div className="flex items-start gap-3 mb-4">
                    <div className={`p-2 rounded-md ${feature.isHighlighted ? 'bg-white/20' : 'bg-primary/10'}`}>
                      {feature.icon}
                    </div>
                    <h2 className="text-xl font-bold">{feature.title}</h2>
                  </div>
                  
                  <p className={`mb-4 flex-grow ${feature.isHighlighted ? 'text-white/90' : 'text-foreground/70'}`}>
                    {feature.description}
                  </p>
                  
                  <Link 
                    href={feature.link} 
                    className={`mt-2 inline-flex items-center ${
                      feature.isHighlighted 
                        ? 'text-white border border-white/30 px-4 py-2 rounded-md hover:bg-white/20 transition-colors' 
                        : 'text-primary hover:text-secondary transition-colors'
                    }`}
                  >
                    <span>{feature.linkText}</span>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-20 mb-10">
            <div className="bg-gradient-to-r from-primary/80 to-secondary/80 rounded-lg p-10 text-white text-center relative overflow-hidden">
              <div className="relative z-10">
                <h2 className="text-3xl font-bold mb-4">Ready to transform your thoracic surgery assessment process?</h2>
                <p className="mb-6 max-w-2xl mx-auto">
                  Our AI-powered tools help ABTS educators create high-quality questions efficiently, matching the exact requirements of thoracic surgery examinations.
                </p>
                <Link href="/generate">
                  <button className="bg-white text-primary px-8 py-4 rounded-md font-bold text-lg hover:bg-white/90 transition-colors duration-300 heartbeat-pulse">
                    Start Generating Questions
                  </button>
                </Link>
              </div>
              
              {/* Background elements */}
              <div className="absolute -top-20 -right-20 w-64 h-64 bg-white/5 rounded-full"></div>
              <div className="absolute -bottom-20 -left-20 w-48 h-48 bg-white/5 rounded-full"></div>
              
              {/* Heart rate line */}
              <div className="absolute bottom-4 left-0 w-full h-8 opacity-20">
                <svg viewBox="0 0 1200 60" xmlns="http://www.w3.org/2000/svg">
                  <path 
                    d="M0,30 L300,30 L320,10 L340,50 L360,10 L380,50 L400,30 L1200,30" 
                    fill="none" 
                    stroke="white" 
                    strokeWidth="2"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-border/40 py-8 bg-background/60 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center mb-4 md:mb-0">
              <Heart className="h-4 w-4 text-primary mr-2" />
              <span className="text-foreground/70">ABTS Unified Generator © {new Date().getFullYear()}</span>
            </div>
            <div className="flex gap-6">
              {["About", "Documentation", "Contact ABTS"].map(item => (
                <a key={item} href="#" className="text-foreground/70 hover:text-primary transition-colors duration-300">
                  {item}
                </a>
              ))}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}