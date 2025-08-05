// OpenNote-inspired Landing Page for Navigo
// Transformed to focus on educational note-taking and learning tools
// Maintains Navigo branding while adopting OpenNote's clean educational aesthetic

import Link from 'next/link';

export default function LandingPageOpenNote() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white relative overflow-hidden">
      
      {/* Floating notebook elements */}
      <div className="writing-elements">
        <div className="pencil"></div>
        <div className="eraser"></div>
        <div className="pen"></div>
      </div>
      
      {/* Floating background pattern */}
      <div className="floating-dots"></div>

      {/* Header */}
      <header className="relative z-20 px-6 lg:px-12 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-sky-400 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">N</span>
            </div>
            <div>
              <div className="font-bold text-xl text-gray-900">Navigo</div>
              <div className="text-xs text-gray-500">Notes & Learning</div>
            </div>
          </div>
          <nav className="hidden md:flex items-center space-x-8">
            <Link href="/features" className="text-gray-600 hover:text-gray-900 transition-colors">Features</Link>
            <Link href="/templates" className="text-gray-600 hover:text-gray-900 transition-colors">Templates</Link>
            <Link href="/pricing" className="text-gray-600 hover:text-gray-900 transition-colors">Pricing</Link>
            <Link href="/login" className="bg-gradient-to-r from-indigo-500 to-sky-400 text-white px-4 py-2 rounded-lg hover:from-indigo-600 hover:to-sky-500 transition-all ink-button">
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-6 lg:px-12 py-20">
        <div className="paper-container">
          <div className="paper-sheet">
            <div className="paper-lines"></div>
            <div className="paper-content">
              
              {/* 3D Notebook Animation */}
              <div className="book mx-auto mb-12">
                <div className="cover">
                  <div className="book-title text-white font-bold">
                    Navigo
                  </div>
                  <div className="book-subtitle text-white text-sm opacity-80">
                    Learning Notebook
                  </div>
                </div>
                <div className="book-content">
                  <h3>Your Digital Notebook</h3>
                  <p>Where every page is a new discovery waiting to be written</p>
                </div>
              </div>
              
              <div className="text-center space-y-8">
                <h1 className="handwritten-title text-5xl lg:text-7xl text-gray-800 mb-6">
                  Bring your learning to life
                </h1>
                
                <div className="ink-pen-line"></div>
                
                <p className="handwritten-text text-gray-600 max-w-2xl mx-auto leading-relaxed">
                  Your learning style is unique—your educational tools should be too. Create your perfect learning environment with Navigo's interactive note-taking and discovery tools.
                </p>
                
                {/* Empty notebook illustration */}
                <div className="my-12 text-center">
                  <div className="inline-block bg-white p-8 rounded-lg shadow-lg border-2 border-dashed border-gray-300 max-w-md">
                    <div className="text-6xl text-gray-300 mb-4">📝</div>
                    <p className="text-gray-400 italic">Everything is yet to be written...</p>
                    <p className="text-sm text-gray-500 mt-2">Your learning journey starts with a blank page</p>
                  </div>
                </div>
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center mt-12">
                  <Link href="/register" className="cta-primary bg-gradient-to-r from-indigo-500 to-sky-400 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 hover:from-indigo-600 hover:to-sky-500 hover:scale-105 hover:shadow-lg ink-button">
                    Start Writing Your Story
                  </Link>
                  <Link href="/demo" className="cta-secondary text-gray-600 hover:text-gray-900 transition-colors px-8 py-4 font-medium text-lg border-2 border-gray-300 rounded-lg hover:border-gray-400 hover:shadow-md ink-button">
                    See How It Works
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Toolkit Section */}
      <section className="px-6 lg:px-12 py-20 bg-gradient-to-b from-white to-gray-50 animate-on-scroll">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="handwritten-title text-4xl lg:text-5xl text-gray-900 mb-4">
              The toolkit that adapts with you
            </h2>
            <div className="ink-pen-line"></div>
            <p className="handwritten-text text-gray-600 max-w-3xl mx-auto mt-6">
              Mix and match custom notes, whiteboards, learning paths, and interactive exercises. Every tool designed to help you learn and discover.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Digital Notes */}
            <div className="feature-card-enhanced">
              <div className="go-corner">
                <div className="go-arrow">→</div>
              </div>
              <div className="feature-icon text-4xl mb-4">📔</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Digital Notes</h3>
              <p className="text-gray-600 text-sm">
                Create, organize, and connect your thoughts with our intelligent note-taking system.
              </p>
              <div className="mt-4 text-xs text-indigo-500 font-semibold">SMART ORGANIZATION</div>
            </div>
            
            {/* Learning Whiteboards */}
            <div className="feature-card-enhanced">
              <div className="go-corner">
                <div className="go-arrow">→</div>
              </div>
              <div className="feature-icon text-4xl mb-4">🖊️</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Interactive Whiteboards</h3>
              <p className="text-gray-600 text-sm">
                Visual thinking spaces where ideas come alive. Draw, diagram, and discover connections.
              </p>
              <div className="mt-4 text-xs text-sky-400 font-semibold">VISUAL LEARNING</div>
            </div>
            
            {/* Learning Paths */}
            <div className="feature-card-enhanced">
              <div className="go-corner">
                <div className="go-arrow">→</div>
              </div>
              <div className="feature-icon text-4xl mb-4">🗺️</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Learning Paths</h3>
              <p className="text-gray-600 text-sm">
                Guided journeys through subjects with checkpoints, challenges, and progress tracking.
              </p>
              <div className="mt-4 text-xs text-indigo-500 font-semibold">GUIDED DISCOVERY</div>
            </div>
            
            {/* Practice Problems */}
            <div className="feature-card-enhanced">
              <div className="go-corner">
                <div className="go-arrow">→</div>
              </div>
              <div className="feature-icon text-4xl mb-4">🧩</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Practice Exercises</h3>
              <p className="text-gray-600 text-sm">
                Interactive problems and challenges that adapt to your learning pace and style.
              </p>
              <div className="mt-4 text-xs text-sky-400 font-semibold">ACTIVE LEARNING</div>
            </div>
          </div>
        </div>
      </section>

      {/* Note-Taking Section */}
      <section className="px-6 lg:px-12 py-20 animate-on-scroll">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Paper sheet mockup */}
            <div className="paper-container">
              <div className="paper-sheet bg-white min-h-96">
                <div className="paper-lines"></div>
                <div className="paper-content">
                  <h3 className="handwritten-title text-3xl text-gray-800 mb-6">Create open notes with our digital note-taking app</h3>
                  <div className="space-y-4 handwritten-text text-gray-600">
                    <p>✏️ Capture ideas as they flow</p>
                    <p>📝 Connect concepts with smart linking</p>
                    <p>🔍 Find anything with intelligent search</p>
                    <p>📚 Organize into meaningful collections</p>
                    <p className="text-gray-400 italic text-sm mt-8">Your thoughts, beautifully organized...</p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Description */}
            <div className="space-y-6">
              <h2 className="handwritten-title text-4xl text-gray-900">
                Focus on interactive note creation and organization
              </h2>
              <div className="ink-pen-line"></div>
              <p className="handwritten-text text-gray-600 leading-relaxed">
                Transform how you capture and connect knowledge. Our note-taking system understands context, suggests connections, and helps you build a personal knowledge graph.
              </p>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="text-green-500 mt-1">✓</div>
                  <span className="text-gray-700">Rich text editing with markdown support</span>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="text-green-500 mt-1">✓</div>
                  <span className="text-gray-700">Smart tagging and auto-categorization</span>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="text-green-500 mt-1">✓</div>
                  <span className="text-gray-700">Real-time collaboration and sharing</span>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="text-green-500 mt-1">✓</div>
                  <span className="text-gray-700">Cross-platform synchronization</span>
                </div>
              </div>
              <Link href="/notes" className="inline-block cta-primary bg-gradient-to-r from-indigo-500 to-sky-400 text-white px-8 py-4 rounded-lg hover:from-indigo-600 hover:to-sky-500 transition-all duration-300 font-semibold hover:scale-105 hover:shadow-lg ink-button">
                Start Taking Notes
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Learning Features Section */}
      <section className="px-6 lg:px-12 py-20 bg-gradient-to-b from-gray-50 to-white animate-on-scroll">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="handwritten-title text-4xl lg:text-5xl text-gray-900 mb-4">
              Watch your lessons come alive
            </h2>
            <div className="ink-pen-line"></div>
            <p className="handwritten-text text-gray-600 max-w-3xl mx-auto mt-6">
              Turn static notes into dynamic learning experiences. Our "Synthesis" feature transforms your written thoughts into interactive lessons and visual connections.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* Visual Learning */}
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-all duration-300 hover:transform hover:scale-105 assessment-card">
              <div className="assessment-icon text-5xl mb-6 text-center">🎨</div>
              <h3 className="handwritten-title text-2xl text-gray-900 mb-4 text-center">Visual Learning</h3>
              <p className="handwritten-text text-gray-600 text-center mb-6">
                Transform notes into mind maps, flowcharts, and interactive diagrams that reveal hidden connections.
              </p>
              <div className="assessment-btn w-full bg-indigo-100 text-indigo-700 py-3 px-6 rounded-lg hover:bg-indigo-200 transition-all text-center font-semibold">
                Explore Visuals
              </div>
            </div>
            
            {/* Interactive Lessons */}
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-all duration-300 hover:transform hover:scale-105 assessment-card">
              <div className="assessment-icon text-5xl mb-6 text-center">⚡</div>
              <h3 className="handwritten-title text-2xl text-gray-900 mb-4 text-center">Interactive Lessons</h3>
              <p className="handwritten-text text-gray-600 text-center mb-6">
                Turn your notes into guided lessons with quizzes, flashcards, and progressive reveals.
              </p>
              <div className="assessment-btn w-full bg-sky-100 text-sky-700 py-3 px-6 rounded-lg hover:bg-sky-200 transition-all text-center font-semibold">
                Try Interactive Mode
              </div>
            </div>
            
            {/* Knowledge Connections */}
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-all duration-300 hover:transform hover:scale-105 assessment-card">
              <div className="assessment-icon text-5xl mb-6 text-center">🕸️</div>
              <h3 className="handwritten-title text-2xl text-gray-900 mb-4 text-center">Knowledge Graph</h3>
              <p className="handwritten-text text-gray-600 text-center mb-6">
                See how your ideas connect across subjects with AI-powered relationship mapping.
              </p>
              <div className="assessment-btn w-full bg-purple-100 text-purple-700 py-3 px-6 rounded-lg hover:bg-purple-200 transition-all text-center font-semibold">
                View Connections
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="px-6 lg:px-12 py-20 animate-on-scroll">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="handwritten-title text-4xl lg:text-5xl text-gray-900 mb-4">
              Learn More, Spend Less
            </h2>
            <div className="ink-pen-line"></div>
            <p className="handwritten-text text-gray-600 max-w-2xl mx-auto mt-6">
              Choose the perfect learning environment for your needs. Start free and grow with advanced features.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Free Tier */}
            <div className="paper-container">
              <div className="paper-sheet bg-white min-h-96 text-center">
                <div className="paper-lines"></div>
                <div className="paper-content">
                  <h3 className="handwritten-title text-2xl text-gray-900 mb-4">Free</h3>
                  <p className="text-gray-600 mb-6">Perfect for trying out Navigo</p>
                  <div className="handwritten-text text-3xl text-gray-900 mb-6">$0</div>
                  <ul className="handwritten-text text-gray-600 space-y-2 mb-8">
                    <li>• 100 notes</li>
                    <li>• Basic templates</li>
                    <li>• Mobile app</li>
                    <li>• Community support</li>
                  </ul>
                  <button className="cta-secondary w-full border-2 border-gray-300 text-gray-700 py-3 px-6 rounded-lg hover:border-gray-400 hover:shadow-md transition-all font-semibold ink-button">
                    Start Free
                  </button>
                </div>
              </div>
            </div>
            
            {/* Premium Tier */}
            <div className="paper-container">
              <div className="paper-sheet bg-gradient-to-br from-indigo-50 to-sky-50 min-h-96 text-center border-2 border-indigo-200">
                <div className="paper-content">
                  <div className="bg-indigo-500 text-white px-3 py-1 rounded-full text-sm font-semibold mb-4 inline-block">Most Popular</div>
                  <h3 className="handwritten-title text-2xl text-gray-900 mb-4">Premium</h3>
                  <p className="text-gray-600 mb-6">Unlock your full learning potential</p>
                  <div className="handwritten-text text-3xl text-gray-900 mb-6">$12<span className="text-base">/month</span></div>
                  <ul className="handwritten-text text-gray-600 space-y-2 mb-8">
                    <li>• Unlimited notes</li>
                    <li>• Advanced templates</li>
                    <li>• AI-powered insights</li>
                    <li>• Priority support</li>
                    <li>• Collaboration tools</li>
                  </ul>
                  <button className="cta-primary w-full bg-gradient-to-r from-indigo-500 to-sky-400 text-white py-3 px-6 rounded-lg hover:from-indigo-600 hover:to-sky-500 transition-all font-semibold hover:scale-105 hover:shadow-lg ink-button">
                    Go Premium
                  </button>
                </div>
              </div>
            </div>
            
            {/* Enterprise Tier */}
            <div className="paper-container">
              <div className="paper-sheet bg-white min-h-96 text-center">
                <div className="paper-lines"></div>
                <div className="paper-content">
                  <h3 className="handwritten-title text-2xl text-gray-900 mb-4">Enterprise</h3>
                  <p className="text-gray-600 mb-6">For schools and institutions</p>
                  <div className="handwritten-text text-3xl text-gray-900 mb-6">Custom</div>
                  <ul className="handwritten-text text-gray-600 space-y-2 mb-8">
                    <li>• Unlimited everything</li>
                    <li>• Custom integrations</li>
                    <li>• Advanced analytics</li>
                    <li>• Dedicated support</li>
                    <li>• SSO & compliance</li>
                  </ul>
                  <button className="cta-secondary w-full border-2 border-gray-300 text-gray-700 py-3 px-6 rounded-lg hover:border-gray-400 hover:shadow-md transition-all font-semibold ink-button">
                    Contact Sales
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 lg:px-12 py-20 bg-gradient-to-br from-indigo-500 to-sky-400 relative overflow-hidden stars-container">
        {/* Stars */}
        <div className="star star-1"></div>
        <div className="star star-2"></div>
        <div className="star star-3"></div>
        <div className="star star-4"></div>
        <div className="star star-5"></div>
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="handwritten-title text-4xl lg:text-6xl text-white mb-6">
            Learning that actually works for you
          </h2>
          <div className="w-32 h-1 bg-white/30 mx-auto rounded mb-8"></div>
          <p className="handwritten-text text-xl text-white/90 max-w-2xl mx-auto mb-12">
            Join thousands of learners who have transformed their study habits with Navigo's intelligent note-taking platform.
          </p>
          
          {/* Features list */}
          <div className="grid md:grid-cols-4 gap-6 mb-12 text-white">
            <div className="space-y-2">
              <div className="text-2xl">📝</div>
              <p className="font-semibold">Create digital open notes</p>
            </div>
            <div className="space-y-2">
              <div className="text-2xl">📚</div>
              <p className="font-semibold">Organize notes efficiently</p>
            </div>
            <div className="space-y-2">
              <div className="text-2xl">🤝</div>
              <p className="font-semibold">Share notes with classmates</p>
            </div>
            <div className="space-y-2">
              <div className="text-2xl">📈</div>
              <p className="font-semibold">Track learning progress</p>
            </div>
          </div>
          
          <Link href="/register" className="cta-primary inline-block bg-white text-indigo-600 px-12 py-4 rounded-lg font-bold text-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 ink-button">
            Try Navigo today
          </Link>
          <p className="handwritten-text text-white/80 mt-4 text-sm">Students crafting tools for students • Free to start</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white py-12 px-6 lg:px-12 border-t border-gray-200">
        <div className="max-w-7xl mx-auto text-center">
          <div className="mb-8">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-sky-400 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">N</span>
              </div>
              <div className="handwritten-title text-2xl text-gray-900">Navigo</div>
            </div>
            <p className="handwritten-text text-gray-600 max-w-2xl mx-auto">
              Digital note-taking platform designed for modern learners. Built with love for education and discovery.
            </p>
          </div>
          
          <div className="border-t border-gray-200 pt-8">
            <p className="text-sm text-gray-500">
              © 2024 Navigo Learning Platform. Crafted for curious minds everywhere.
              <br />
              <span className="italic">Where every note becomes a stepping stone to knowledge.</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}