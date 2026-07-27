// data/changelogData.ts

export const changelogData = [
  {
    version: "v1.1.0",
    date: "10 July 2026",
    changes: [
      {
        type: "feature", 
        title: "LLM Context Filtering Update",
        description: "Migrated the natural language processor to GPT OSS 20B. Previously was using Llama 70b which was depreciated."
      },
      {
        type: "feature", 
        title: "Added About and Changelog Pages",
        description: "Added the hamburger menu containing the About and Changelogs pages."
      },
      {
        type: "fix",
        title: "Resolved False Positives",
        description: "Fixed an edge case where chronic complaints (like potholes or garbage) were being falsely flagged as current disruptions."
      },
      {
        type: "Upcoming", 
        title: "Upcoming Update",
        description: "Users will be able to filter news by tags like 'Power', 'Water', 'Traffic', etc."
      }
    ]
  },
  {
    version: "v1.0.0",
    date: "01 July 2026",
    changes: [
      {
        type: "feature",
        title: "App Launch",
        description: "Deployed the automated Bengaluru Civic Updates dashboard featuring real time news about city disruptions."
      }
    ]
  }
];