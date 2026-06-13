import os
import json
import time
from groq import Groq
from google import genai
from google.genai import types

# Initialize both clients using environment variables
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Defining the disruption keywords here to fix/prevent infinite loop in the files. Previously, both files kept calling each other.

DETERMINISTIC_KEYWORDS = [
    "bangalore", "bengaluru", "ooru", "namma ooru", "blr", "tech capital of india", "silicon valley of india", "it hub",
    "bbmp", "bescom", "bwssb", "bmrc", "namma metro", "bmtc", "bmrcl", "gba",
    "btp", "bengaluru traffic police", "bcp", "bengaluru police", "bengaluru city police",
    "north bengaluru", "south bengaluru", "east bengaluru", "west bengaluru", "kr pura", "kr puram", "church street", "koramangala", "whitefield", "electronic city", "marathahalli", "yelahanka", "hebbal",
    "btm layout", "jp nagar", "indiranagar", "hsr layout"
    ]

DISRUPTION_KEYWORDS = [
    "bbmp", "bescom", "bwssb", "bmrc", "namma metro", "bmtc", "bmrcl", "gba", 
    "road closure", "road repair", "road maintainence", "road construction", "road work", "road closed",
     "traffic", "collision", "pileup", "traffic jam", "congestion", "diversion", "disruption",
    "metro delay", "metro disruption", "metro maintenance", "metro work", "metro closed",
    "bus delay", "bus disruption", "bus maintenance", "bus strike", "bmtc strike",
    "garbage", "waste", "garbage collection", "garbage strike", "garbage disruption", "sanitation",
    "water cut", "water disruption", "water work", "water closed", "water supply", "water shortage",
    "power cut", "power disruption", "grid work", "grid maintenance", "scheduled power cut", "scheduled power disruption", "scheduled grid work", "scheduled grid maintenance", "scheduled power cut", "scheduled power disruption",
    "holiday", "public holiday", "bank holiday", "school holiday", "festival", "event hliday",
    "bandh", "statewide", "city wide", "citywide",
    "monsoon alert", "weather disruption", "flooding", "water logging",
    "delay", "disruption", "maintenance", "closed", "inconvenience", "shortage",
    "strike", "protest", "dharna", "agitation", "rally", "march"
    ]

SYSTEM_PROMPT = """
        You are a precise civic data classifier for Bengaluru or Bangalore. Analyze the provided news headline and description. 
        Determine if it represents an actionable, ongoing, or persistent physical disruption to everyday life in Bengaluru.

        Use this list of targeted civic concepts and organizations as a guide for what falls within our monitoring scope:
        {", ".join(civic_keywords)}

        Strict Rules:
        1. GEOGRAPHY: The disruption MUST be inside Bengaluru. CONFIRM location existance inside Bengaluru before going ahead when locations are mentioned. If the landmarks, roads, or areas mentioned are outside Bengaluru, set is_disruption to false. Make no mistakes.
        2. ACTIONABILITY: Focus on ongoing, upcoming, or persistent disruptions. Exclude resolved, one-off historical events unless they cause lasting infrastructure damage.

        You must respond strictly in JSON format matching this exact schema:
        {{
        "is_disruption": true or false,
        "category": "Traffic" | "Power" | "Water" | "Weather" | "Infrastructure" | "None",
        "confidence_score": 0.0 to 1.0,
        "reasoning": "A one sentence explanation focusing on location and actionability."
        }}
"""
# Using double curly braces becasue we want python to treat them as literal text instead of trying to evaluate them as code blocks.

def get_disruption_context(headline, description):
    """
    Evaluates news text. Tries Groq (Llama 3.3) first, falls back to Google (Gemini) if Groq fails.
    """
    # ----- PRIMARY: GROQ (LLAMA 3.3) -----
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Headline: {headline}\nDescription: {description}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0                                   # Ensures the model gives a logical output rather than a creative one.
        )

        groq_result = json.loads(chat_completion.choices[0].message.content)     #Save the result so we can evalulate confidence score.
        
        # Check if the model is uncertain about its decision
        confidence = groq_result.get("confidence_score", 0.0)                   # The 0.0 default ensures that if the model's response doesn't include a confidence score, it will be treated as 0 confidence but will not crash the program due to a missing key.
        if confidence < 0.8:
            print(f" !!! Low confidence from Groq ({confidence}) with result: {groq_result.get('is_disruption')}. Routing to Gemini for review...")
            # Raising an error intentionally forces execution into the 'except' block below
            raise ValueError("Confidence score below threshold")

        return groq_result
        
    except Exception as groq_error:
        print(f"Primary API (Groq) failed: {groq_error}. \n Initiating Gemini fallback...")
        
        # ----- FALLBACK: GOOGLE (GEMINI) -----
        try:
            time.sleep(13) # Respecting Gemini's strict 5 requests per minute limit
            
            response = gemini_client.models.generate_content(
                model='gemini-3.5-flash',
                contents=f"Headline: {headline}\nDescription: {description}",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0                           # Ensures the model gives a logical output rather than a creative one.
                )
            )
            return json.loads(response.text)
            
        except Exception as gemini_error:
            print(f"Fallback API (Gemini) also failed: {gemini_error}.")

            # Using Groq's original result since Gemini failed. Cannot reject an article just because even the fallback failed for whatever reason.
            if groq_result:
                print("Reverting to Groq's original result")
                return groq_result
            
            return {
                "is_disruption": False, 
                "category": "Error", 
                "confidence_score": 0.0,
                "reasoning": "Both LLM APIs failed to respond."
            }