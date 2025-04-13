"use client";

import { useEffect, useState } from "react";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [mounted, setMounted] = useState(false);
  
  // Handle initial page load animation
  useEffect(() => {
    setMounted(true);
    
    // Add a smooth page transition effect
    document.body.style.opacity = "0";
    setTimeout(() => {
      document.body.style.opacity = "1";
    }, 10);
    
    return () => {
      document.body.style.transition = "opacity 300ms ease";
    };
  }, []);

  return (
    <html lang="en" suppressHydrationWarning className="dark">
      <head>
        <title>ABTS Unified Generator</title>
        <meta name="description" content="Create high-quality thoracic surgery assessment questions with AI" />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased transition-opacity duration-300 ${
          mounted ? "opacity-100" : "opacity-0"
        }`}
      >
        <div className="min-h-screen flex flex-col relative">
          {/* Animated background gradient blobs */}
          <div 
            className="fixed inset-0 -z-10 opacity-20 pointer-events-none overflow-hidden"
            aria-hidden="true"
          >
            <div className="absolute top-1/4 -left-1/4 w-1/2 h-1/2 bg-gradient-to-br from-primary/40 to-secondary/40 rounded-full blur-3xl animate-blob"></div>
            <div className="absolute bottom-1/3 -right-1/4 w-1/2 h-1/2 bg-gradient-to-bl from-accent/30 to-primary/30 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
            <div className="absolute top-2/3 left-1/3 w-1/3 h-1/3 bg-gradient-to-tr from-secondary/30 to-accent/30 rounded-full blur-3xl animate-blob animation-delay-4000"></div>
          </div>
          
          {children}
        </div>
      </body>
    </html>
  );
}