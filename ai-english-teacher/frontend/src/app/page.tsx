import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
        <span className="text-xl font-bold text-primary">AI English Teacher</span>
        <div className="flex gap-4">
          <Link href="/login" className="px-4 py-2 text-sm font-medium hover:text-primary">Login</Link>
          <Link href="/register" className="px-4 py-2 text-sm font-medium bg-primary text-white rounded-lg hover:bg-primary/90">
            Get Started
          </Link>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-20 text-center">
        <h1 className="text-5xl font-bold tracking-tight text-gray-900 mb-6">
          Master English with AI
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-10">
          Personalized training for IELTS, PTE, TOEFL, and Corporate English.
          Get CEFR-level assessment, role-play practice, and AI-powered feedback.
        </p>
        <div className="flex flex-wrap gap-4 justify-center">
          <Link href="/register" className="px-8 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90">
            Start Free Assessment
          </Link>
          <Link href="/conversation" className="px-8 py-3 border border-gray-300 rounded-lg font-medium hover:bg-white">
            Voice Practice
          </Link>
          <Link href="/grammar-class" className="px-8 py-3 border border-gray-300 rounded-lg font-medium hover:bg-white">
            Grammar Class
          </Link>
          <Link href="/dashboard/student" className="px-8 py-3 border border-gray-300 rounded-lg font-medium hover:bg-white">
            View Dashboard
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20">
          {[
            { title: '6-Skill Assessment', desc: 'Grammar, vocabulary, writing, reading, listening, and speaking evaluation with CEFR mapping.' },
            { title: 'AI Role-Play', desc: 'Practice real-world scenarios with an adaptive AI teacher that remembers your mistakes.' },
            { title: 'Progress Tracking', desc: 'IELTS, PTE, and CEFR trend charts with personalized learning plans.' },
          ].map((f) => (
            <div key={f.title} className="bg-white rounded-xl p-6 shadow-sm border">
              <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
              <p className="text-gray-600 text-sm">{f.desc}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
