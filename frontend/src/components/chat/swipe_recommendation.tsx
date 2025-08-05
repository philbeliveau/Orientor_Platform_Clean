'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const jobs = [
  {
    title: "UX Designer",
    industry: "🎨 Design & Tech",
    what: "Sketch screens, build clickable prototypes, and test ideas to make apps and websites easier and more fun to use.",
    why: "You love drawing, organizing things, or wondering “why did they design it like *that*?”",
  },
  {
    title: "Data Analyst",
    industry: "📊 Science & Business",
    what: "Collect and analyze data (like survey results or app usage) to spot patterns and help teams make smart choices.",
    why: "You like solving puzzles, working with numbers, or figuring out how things connect.",
  },
  {
    title: "Frontend Developer",
    industry: "💻 Web & Code",
    what: "Turn designs into interactive websites using HTML, CSS, and JavaScript. It's part tech, part creativity.",
    why: "You enjoy coding, building online, or seeing your work come to life on screen.",
  },
  {
    title: "Content Strategist",
    industry: "📝 Media & Communication",
    what: "Plan and write content for websites, social media, or emails. Decide what to say and how to say it.",
    why: "You enjoy writing, storytelling, or coming up with ideas people want to click on.",
  },
];

export default function JobSwipeCard() {
  const [index, setIndex] = useState(0);

  const handleNext = () => {
    setIndex((prev) => (prev + 1 < jobs.length ? prev + 1 : 0));
  };

  const handleSave = () => {
    // Add save logic here if needed
    handleNext();
  };

  return (
    <div className="min-h-screen bg-transparent flex flex-col items-center justify-center px-4">
      <h2 className="text-4xl font-bold text-gray-900 mb-2 text-center">Your Match based on your profile</h2>
      <p className="text-3sm text-neutral-600 text-center mb-2 max-w-xs">
        Swipe through careers you might love.
      </p>

      <div className="w-[320px] h-[500px] relative">
        <AnimatePresence>
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.4 }}
            className="absolute inset-0 bg-white border border-gray-200 rounded-3xl shadow-xl p-5 flex flex-col justify-between"
          >
            <div className="whitespace-pre-wrap">
              <h3 className="text-xl font-bold text-gray-800">{jobs[index].title}</h3>
              <p className="text-sm text-indigo-600 mt-1">{jobs[index].industry}</p>

              <div className="mt-4 text-sm text-gray-700 space-y-3">
                <div>
                  <p className="font-semibold text-gray-800 mb-1 text-xs">✨ What You'll Do</p>
                  <p className="text-xs">{jobs[index].what}</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-800 mb-1 text-xs">💡 Why It Might Fit You</p>
                  <p className="text-xs">{jobs[index].why}</p>
                </div>
              </div>
            </div>

            <div className="flex justify-between mt-6">
              <button
                onClick={handleNext}
                className="text-yellow-500 border border-yellow-300 rounded-full px-4 py-1 hover:bg-yellow-50 transition"
              >
                Skip
              </button>
              <button
                onClick={handleSave}
                className="text-blue-600 border border-blue-300 rounded-full px-4 py-1 hover:bg-blue-50 transition"
              >
                Save
              </button>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
