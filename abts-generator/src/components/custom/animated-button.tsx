"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { cva, type VariantProps } from "class-variance-authority";

const animatedButtonVariants = cva(
  "relative overflow-hidden inline-flex items-center justify-center transition-all duration-300",
  {
    variants: {
      animation: {
        none: "",
        slide: "group",
        pulse: "btn-pulse",
        gradient: "gradient-button",
        glow: "glow-on-hover",
        bounce: "hover:animate-bounce",
        grow: "transform hover:scale-105",
      },
      shape: {
        default: "rounded-md",
        pill: "rounded-full",
        square: "rounded-none",
      },
    },
    defaultVariants: {
      animation: "slide",
      shape: "default",
    },
  }
);

export interface AnimatedButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof animatedButtonVariants> {
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
  asChild?: boolean;
}

export const AnimatedButton = React.forwardRef<HTMLButtonElement, AnimatedButtonProps>(
  ({ className, variant, size, animation, shape, children, ...props }, ref) => {
    return (
      <Button
        className={cn(
          animatedButtonVariants({ animation, shape }),
          className
        )}
        variant={variant}
        size={size}
        ref={ref}
        {...props}
      >
        <span className="relative z-10">{children}</span>
        {animation === "slide" && (
          <span className="absolute inset-0 bg-white/20 transform -translate-x-full group-hover:translate-x-0 transition-transform duration-300"></span>
        )}
        {animation === "glow" && (
          <span className="absolute inset-0 bg-gradient-to-r from-primary/0 via-primary/30 to-primary/0 -translate-x-full animate-shimmer"></span>
        )}
      </Button>
    );
  }
);

AnimatedButton.displayName = "AnimatedButton";