// app/changelogs/page.tsx

import { changelogData } from '@/data/changelogData'; // Adjust path if needed
import Link from 'next/link';

export default function Changelogs() {
  return (
    <div className="min-h-screen bg-black text-gray-200 p-6 md:p-12 font-sans">
      <div className="max-w-3xl mx-auto">
        
        {/* Header Section */}
        <div className="mb-12">
          <Link href="/" className="text-gray-400 hover:text-white mb-6 inline-block transition-colors">
            ← Back to Updates
          </Link>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <svg className="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Changelog
          </h1>
          <p className="text-gray-400 mt-2 ml-11">What's new in Bengaluru Civic Updates</p>
        </div>

        {/* Timeline Container */}
        <div className="relative border-l-2 border-gray-800 ml-4 md:ml-6 space-y-12 pb-12">
          {changelogData.map((release, index) => (
            <div key={index} className="relative pl-8 md:pl-12">
              
              {/* Timeline Node (The blue circle on the line) */}
              <div className="absolute -left-[9px] top-1.5 w-4 h-4 rounded-full bg-blue-500 ring-4 ring-black"></div>
              
              {/* Version & Date */}
              <div className="flex items-baseline gap-3 mb-6">
                <h2 className="text-xl font-bold text-white">{release.version}</h2>
                <span className="text-sm text-gray-500">{release.date}</span>
              </div>

              {/* Changes List */}
              <ul className="space-y-6">
                {release.changes.map((change, changeIndex) => (
                  <li key={changeIndex} className="relative pl-6">
                    {/* Color-coded bullet point */}
                    <span 
                      className={`absolute left-0 top-2.5 w-2 h-2 rounded-full ${
                        change.type === 'feature' ? 'bg-blue-400' : 
                        change.type === 'fix' ? 'bg-pink-500' : 'bg-green-400'
                      }`}
                    ></span>
                    
                    <h3 className="text-base font-semibold text-gray-200 mb-1">
                      {change.title}
                    </h3>
                    <p className="text-sm text-gray-400 leading-relaxed">
                      {change.description}
                    </p>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}