"use client"

import { useState, useEffect } from 'react'
import { useTheme } from 'next-themes'

export default function Home() {
  const [news, setNews] = useState([])
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Fetch data from FastAPI on load
  useEffect(() => {
    setMounted(true)
    fetch('http://127.0.0.1:8000/news')
      .then(res => res.json())
      .then(data => setNews(data))
      .catch(err => console.error("Failed to fetch news:", err))
  }, [])

  if (!mounted) return null

  return (
    <main className="max-w-2xl mx-auto border-x border-gray-200 dark:border-gray-800 min-h-screen">
      
      {/* Sticky Header with Theme Toggle */}
      <header className="sticky top-0 z-10 backdrop-blur-md bg-white/80 dark:bg-black/80 border-b border-gray-200 dark:border-gray-800 p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">Bengaluru Civic Updates</h1>
        <button 
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors text-xl"
          title="Toggle Theme"
        >
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
      </header>

      {/* The News Feed */}
      <div className="flex flex-col">
        {news.map((item: any) => (
          <article 
            key={item.id} 
            className="p-4 border-b border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900/50 transition-colors cursor-pointer"
            onClick={() => window.open(item.link, '_blank')}
          >
            <div className="flex gap-4">
              
              {/* Avatar Placeholder */}
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-blue-600 dark:text-blue-300 font-bold">
                  B
                </div>
              </div>

              {/* Content Column */}
              <div className="flex-1 min-w-0">
                
                {/* Meta Row: Date & Category Tag */}
                <div className="flex items-center gap-2 mb-1 text-sm text-gray-500 dark:text-gray-400">
                  <span className="font-semibold text-gray-900 dark:text-white truncate">
                    Civic Source
                  </span>
                  <span>·</span>
                  <time dateTime={item.published}>
                    {new Date(item.published).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </time>
                  <span>·</span>
                  <span className="bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 px-2 py-0.5 rounded-full text-xs font-medium">
                    Update
                  </span>
                </div>

                {/* Headline / Title */}
                <h2 className="text-base font-medium text-gray-900 dark:text-gray-100 mb-2 leading-snug">
                  {item.title}
                </h2>

                {/* Body / Description */}
                <div 
                  className="text-sm text-gray-600 dark:text-gray-300 line-clamp-4"
                  dangerouslySetInnerHTML={{ __html: item.description }} 
                />
              </div>
            </div>
          </article>
        ))}
      </div>
    </main>
  )
}