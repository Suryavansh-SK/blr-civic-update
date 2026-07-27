// app/about/page.tsx

import Link from 'next/link';

export default function About() {
  return (
    <div className="min-h-screen bg-black text-gray-200 p-6 md:p-12 font-sans">
      <div className="max-w-3xl mx-auto">
        
        <Link href="/" className="text-gray-400 hover:text-white mb-8 inline-block transition-colors">
          ← Back to Updates
        </Link>
        
        <h1 className="text-3xl font-bold text-white mb-8">About This Project</h1>
        
        <div className="space-y-6 text-lg text-gray-300 leading-relaxed text-justify">
          <p>
            Bengaluru Civic Updates is a centralized dashboard that aggregates announced infrastructure disruptions and public service halts across the city.
          </p>
          <p>
            The system constantly monitors local news agencies and official announcements from key civic authorities, including BESCOM, BWSSB, BMRCL, BMTC, the Bangalore Traffic Police, and the GBA.
          </p>
          <p>
            By filtering out the noise, it provides a clean, real-time feed of verified, ongoing, or upcoming disruptions related to transit, power, water, weather, and road closures all in one place.
          </p>
          
          <div className="mt-12 pt-8 border-t border-gray-800">
            <h2 className="text-xl font-bold text-white mb-4">Under the Hood</h2>
            <ul className="list-disc pl-5 space-y-2 text-base text-gray-400">
              <li>Built with Next.js and Tailwind CSS</li>
              <li>Data aggregation via Python and GitHub Actions</li>
              <li>Context filtering powered by GPT OSS 20B and Gemini 3.5 Flash</li>
              <li>Database architecture hosted on Supabase</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}