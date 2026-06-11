from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Locate and load the .env file in the api folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, '.env'))

app = FastAPI(title="BLRCivicUpdate API")

# --- CORS (Cross-Origin Resource Sharing) VIP PASS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Allows Next.js app to connect
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

@app.get("/")
def root():
    return {"status": "online", "message": "API is actively listening."}

@app.get("/news")
def get_civic_news():
    try:
        # Connect to Supabase
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Fetch the latest 50 articles
        cursor.execute("SELECT * FROM civic_news ORDER BY published_parsed DESC LIMIT 50;")
        records = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Format published_parsed as ISO string for frontend compatibility
        # for record in records:
        #     record.update({"published_parsed": record["published_parsed"].isoformat()})
        #     # record['published_parsed'] = record['published_parsed'].isoformat()
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))