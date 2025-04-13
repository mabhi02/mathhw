"use client";

import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface AnimatedCardProps extends React.ComponentProps<typeof Card> {
  glowOnHover?: boolean;
  hoverScale?: boolean;
  topBorder?: boolean;
  hoverBorder?: boolean;
  depth?: "none" | "sm" | "md" | "lg";
  children: React.ReactNode;
}

export function AnimatedCard({
  glowOnHover = false,
  hoverScale = true,
  topBorder = true,
  hoverBorder = true,
  depth = "sm",
  className,
  children,
  ...props
}: AnimatedCardProps) {
  const [isMounted, setIsMounted] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);
  const [rotation, setRotation] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current || !isHovering) return;
    
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    const rotateX = (y - centerY) / 20;
    const rotateY = (centerX - x) / 20;
    
    setRotation({ x: rotateX, y: rotateY });
  };

  const handleMouseEnter = () => {
    setIsHovering(true);
  };

  const handleMouseLeave = () => {
    setIsHovering(false);
    setRotation({ x: 0, y: 0 });
  };

  const depthStyles = {
    none: "",
    sm: "shadow-sm hover:shadow",
    md: "shadow hover:shadow-md",
    lg: "shadow-md hover:shadow-lg",
  };

  return (
    <Card
      ref={cardRef}
      className={cn(
        "transition-all duration-300",
        isMounted ? "opacity-100" : "opacity-0 translate-y-4",
        hoverScale && "hover:-translate-y-1",
        depthStyles[depth],
        glowOnHover && isHovering && "glow-effect",
        topBorder && "border-t-2 border-t-primary",
        hoverBorder && "hover:border-primary",
        isHovering && "z-10",
        className
      )}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{
        transform: isHovering 
          ? `perspective(1000px) rotateX(${rotation.x}deg) rotateY(${rotation.y}deg)` 
          : "perspective(1000px) rotateX(0) rotateY(0)",
      }}
      {...props}
    >
      {children}
    </Card>
  );
}

export { CardContent, CardDescription, CardFooter, CardHeader, CardTitle };