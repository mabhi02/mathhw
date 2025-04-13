// File: src/app/page.tsx
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-gray-200 py-4">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center">
            <div className="text-xl font-bold text-primary">ABTS Generator</div>
            <nav className="hidden md:flex space-x-4">
              <Link href="/outlines" className="hover:text-primary">Outlines</Link>
              <Link href="/templates" className="hover:text-primary">Templates</Link>
              <Link href="/questions" className="hover:text-primary">Questions</Link>
              <Link href="/comparisons" className="hover:text-primary">Comparisons</Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">ABTS Unified Generator</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Streamline the creation of high-quality medical assessment questions with AI-powered generation tools.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {/* Feature 1 */}
          <div className="border rounded-lg p-6 hover:shadow-md transition-shadow">
            <h2 className="text-xl font-bold mb-2">Content Outlines</h2>
            <p className="text-gray-600 mb-4">
              Manage structured content outlines for organized question generation
            </p>
            <Link href="/outlines" className="text-primary hover:underline">Explore Outlines →</Link>
          </div>

          {/* Feature 2 */}
          <div className="border rounded-lg p-6 hover:shadow-md transition-shadow">
            <h2 className="text-xl font-bold mb-2">Question Templates</h2>
            <p className="text-gray-600 mb-4">
              Standardize your question formats with customizable templates
            </p>
            <Link href="/templates" className="text-primary hover:underline">Browse Templates →</Link>
          </div>

          {/* Feature 3 */}
          <div className="border rounded-lg p-6 hover:shadow-md transition-shadow">
            <h2 className="text-xl font-bold mb-2">Question Generation</h2>
            <p className="text-gray-600 mb-4">
              Generate high-quality medical questions using AI
            </p>
            <Link href="/generate" className="text-primary hover:underline">Generate Questions →</Link>
          </div>

          {/* Feature 4 */}
          <div className="border rounded-lg p-6 hover:shadow-md transition-shadow">
            <h2 className="text-xl font-bold mb-2">Question Library</h2>
            <p className="text-gray-600 mb-4">
              Browse, filter, and manage your generated questions
            </p>
            <Link href="/questions" className="text-primary hover:underline">View Questions →</Link>
          </div>

          {/* Feature 5 */}
          <div className="border rounded-lg p-6 hover:shadow-md transition-shadow">
            <h2 className="text-xl font-bold mb-2">A/B Comparisons</h2>
            <p className="text-gray-600 mb-4">
              Compare direct vs. agent-based question generation approaches
            </p>
            <Link href="/comparisons" className="text-primary hover:underline">View Comparisons →</Link>
          </div>

          {/* Feature 6 */}
          <div className="bg-primary text-white border rounded-lg p-6 hover:shadow-md transition-shadow">
            <h2 className="text-xl font-bold mb-2">Get Started</h2>
            <p className="mb-4">
              Begin generating questions now with our AI-powered tools
            </p>
            <Link href="/generate" className="bg-white text-primary px-4 py-2 rounded-md inline-block">
              Start Now →
            </Link>
          </div>
        </div>
      </main>

      <footer className="border-t border-gray-200 py-4">
        <div className="container mx-auto px-4 text-center text-gray-600">
          ABTS Unified Generator &copy; {new Date().getFullYear()}
        </div>
      </footer>
    </div>
  );
}