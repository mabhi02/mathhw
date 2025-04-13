"use client";

import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

type FadeInProps = {
  children: React.ReactNode;
  direction?: 'up' | 'down' | 'left' | 'right';
  delay?: number;
  duration?: number;
  className?: string;
  distance?: number;
  threshold?: number;
  once?: boolean;
};

export function FadeIn({
  children,
  direction = 'up',
  delay = 0,
  duration = 500,
  className = '',
  distance = 20,
  threshold = 0.1,
  once = true,
}: FadeInProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [ref, setRef] = useState<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!ref) return;
    
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (once) observer.unobserve(ref);
        } else if (!once) {
          setIsVisible(false);
        }
      },
      {
        threshold,
      }
    );

    observer.observe(ref);
    return () => {
      if (ref) observer.unobserve(ref);
    };
  }, [ref, once, threshold]);

  const directionStyles = {
    up: { transform: `translateY(${distance}px)` },
    down: { transform: `translateY(-${distance}px)` },
    left: { transform: `translateX(${distance}px)` },
    right: { transform: `translateX(-${distance}px)` },
  };

  const animationStyles = {
    opacity: isVisible ? 1 : 0,
    transform: isVisible ? 'translate(0, 0)' : directionStyles[direction].transform,
    transition: `opacity ${duration}ms ease-out, transform ${duration}ms ease-out`,
    transitionDelay: `${delay}ms`,
  };

  return (
    <div
      ref={setRef}
      className={className}
      style={animationStyles}
    >
      {children}
    </div>
  );
}

type StaggerChildrenProps = {
  children: React.ReactNode[];
  staggerDelay?: number;
  containerClassName?: string;
  childClassName?: string;
  direction?: 'up' | 'down' | 'left' | 'right';
  duration?: number;
  distance?: number;
  initialDelay?: number;
};

export function StaggerChildren({
  children,
  staggerDelay = 100,
  containerClassName = '',
  childClassName = '',
  direction = 'up',
  duration = 500,
  distance = 20,
  initialDelay = 0,
}: StaggerChildrenProps) {
  return (
    <div className={containerClassName}>
      {React.Children.map(children, (child, index) => (
        <FadeIn
          key={index}
          direction={direction}
          delay={initialDelay + index * staggerDelay}
          duration={duration}
          className={childClassName}
          distance={distance}
        >
          {child}
        </FadeIn>
      ))}
    </div>
  );
}

type FloatingElementProps = {
  children: React.ReactNode;
  amplitude?: number;
  period?: number;
  className?: string;
  phase?: number;
};

export function FloatingElement({
  children,
  amplitude = 10,
  period = 3,
  className = '',
  phase = 0,
}: FloatingElementProps) {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div
      className={cn(
        'transition-opacity duration-300',
        mounted ? 'opacity-100' : 'opacity-0',
        className
      )}
      style={{
        animation: `float ${period}s ease-in-out infinite`,
        animationDelay: `${phase}s`,
      }}
    >
      {children}
    </div>
  );
}

type ScrollRevealWrapperProps = {
  children: React.ReactNode;
  className?: string;
  threshold?: number;
  once?: boolean;
};

export function ScrollRevealWrapper({
  children,
  className = '',
  threshold = 0.1,
  once = true,
}: ScrollRevealWrapperProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [ref, setRef] = useState<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!ref) return;
    
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (once) observer.unobserve(ref);
        } else if (!once) {
          setIsVisible(false);
        }
      },
      {
        threshold,
      }
    );

    observer.observe(ref);
    return () => {
      if (ref) observer.unobserve(ref);
    };
  }, [ref, once, threshold]);

  return (
    <div
      ref={setRef}
      className={cn(
        'transition-all duration-700',
        isVisible ? 'opacity-100 transform-none' : 'opacity-0 translate-y-10',
        className
      )}
    >
      {children}
    </div>
  );
}

export function GradientText({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <span 
      className={cn(
        "bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent",
        className
      )}
    >
      {children}
    </span>
  );
}

export function PulseEffect({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("btn-pulse", className)}>
      {children}
    </div>
  );
}