// File: abts-generator/src/components/layout/main-layout.tsx
import { Navbar } from "@/components/layout/navbar";

export function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-6">
        {children}
      </main>
      <footer className="border-t py-4 text-center text-sm text-muted-foreground">
        <div className="container mx-auto">
          ABTS Unified Generator &copy; {new Date().getFullYear()}
        </div>
      </footer>
    </div>
  );
}