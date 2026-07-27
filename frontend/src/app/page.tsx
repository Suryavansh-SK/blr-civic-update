"use client"

import { useState, useEffect } from 'react'
import Link from 'next/link'

const formatDate = (dateString: string) => {
  if (!dateString) return 'Unknown Date'
  const date = new Date(dateString)
  
  if (isNaN(date.getTime())) return 'Recent' 

  const day = String(date.getDate()).padStart(2, '0')
  const month = date.toLocaleString('en-GB', { month: 'short' })
  const year = date.getFullYear()
  
  return `${day}/${month}/${year}`
}

export default function Home() {
  const [news, setNews] = useState([])
  const [mounted, setMounted] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    setMounted(true)
    
    // The "as string" assertion tells TypeScript to stop worrying about undefined values
    const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL as string
    const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY as string

    // Fetching directly from the Supabase REST API, ordering by published date
    fetch(`${SUPABASE_URL}/rest/v1/civic_news?select=*&order=published.desc`, {
      headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
      }
    })
      .then(res => res.json())
      .then(data => setNews(data))
      .catch(err => console.error("Failed to fetch news:", err))
  }, [])

  if (!mounted) return null

  return (
    <main className="max-w-2xl mx-auto min-h-screen bg-[#0a0a0a] border-x border-gray-900">
      
      <header className="sticky top-0 z-10 backdrop-blur-md bg-black/80 border-b border-gray-800 p-4 flex justify-between items-center relative">
        
        {/* Title acts as the persistent Home button */}
        <Link href="/" className="text-xl font-bold text-white hover:text-gray-300 transition-colors">
          Bengaluru Civic Updates
        </Link>

        {/* Hamburger Icon Button */}
        <button 
          onClick={() => setMenuOpen(!menuOpen)} 
          className="p-2 text-gray-400 hover:text-white transition-colors focus:outline-none"
          aria-label="Toggle menu"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {menuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>

        {/* Dropdown Menu */}
        {menuOpen && (
          <nav className="absolute top-full right-4 mt-2 w-48 bg-[#111] border border-gray-800 rounded-xl shadow-2xl py-2 flex flex-col z-20">
             <Link 
               href="/about" 
               className="px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
             >
               About
             </Link>
             <Link 
               href="/changelogs" 
               className="px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
             >
               Changelogs
             </Link>
          </nav>
        )}
      </header>

      <div className="flex flex-col gap-4 p-4">
        {news.map((item: any) => (
          <article 
            key={item.id} 
            className="p-4 bg-black border border-gray-800 rounded-xl shadow-sm hover:border-gray-700 transition-colors cursor-pointer"
            onClick={() => window.open(item.link, '_blank')}
          >
            <div className="flex flex-col min-w-0">
              
              <div className="flex items-center gap-2 mb-2 text-sm text-gray-400">
                <time dateTime={item.published}>
                  {formatDate(item.published)}
                </time>
                <span>·</span>
                <span className="bg-blue-900/30 text-blue-400 px-2.5 py-0.5 rounded-md text-xs font-semibold uppercase tracking-wider">
                  {item.category || 'Update'}
                </span>
              </div>

              <h2 className="text-base font-medium text-gray-100 mb-2 leading-snug">
                {item.title}
              </h2>

              <div 
                className="text-sm text-gray-400 line-clamp-4"
                dangerouslySetInnerHTML={{ __html: item.description }} 
              />
            </div>
          </article>
        ))}
      </div>
    </main>
  )
}