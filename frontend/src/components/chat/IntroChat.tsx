// components/IntroChat.tsx
'use client';
import { useRouter } from 'next/router';

export default function IntroChat() {
  const router = useRouter();
  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 max-w-md mx-auto">
      <h2 className="text-xl font-bold mb-4">Unsure of your path?</h2>
      <p className="mb-4">Let’s chat and uncover what could be right for you.</p>
      <button 
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
        onClick={() => router.push('/chat')}
      >
        Start the conversation
      </button>
    </div>
  );
}
