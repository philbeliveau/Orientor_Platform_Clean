import { SignUp } from '@clerk/nextjs'

export default function Page() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Join Orientor</h1>
          <p className="text-gray-600">Start your AI-powered career guidance journey</p>
        </div>
        <SignUp 
          appearance={{
            elements: {
              formButtonPrimary: 'bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors',
              card: 'shadow-xl border-0 rounded-xl bg-white p-8',
              headerTitle: 'text-2xl font-bold text-gray-900',
              headerSubtitle: 'text-gray-600',
              socialButtonsBlockButton: 'border border-gray-300 rounded-lg hover:bg-gray-50',
              formFieldInput: 'border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }
          }}
          afterSignUpUrl="/dashboard"
          signInUrl="/sign-in"
          routing="path"
          path="/sign-up"
        />
      </div>
    </div>
  )
}