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
    "power cut", "power outage", "power disruption", "grid work", "grid maintenance", "scheduled power cut", "scheduled power disruption", "scheduled grid work", "scheduled grid maintenance", "scheduled power cut", "scheduled power disruption", "scheduled power outage",
    "holiday", "public holiday", "bank holiday", "school holiday", "festival", "event hliday",
    "bandh", "statewide", "city wide", "citywide",
    "monsoon alert", "weather disruption", "flooding", "water logging",
    "delay", "disruption", "maintenance", "closed", "inconvenience", "shortage",
    "strike", "protest", "dharna", "agitation", "rally", "march"
    ]

SYSTEM_PROMPT = f"""
        You are a highly strict filtering algorithm for Bengaluru or Bangalore. Analyze the provided news headline and description. 
        Determine if it represents an ACTIVE, ONGOING, or UPCOMING physical disruptions to everyday public life.


        Strict Rules for REJECTION (Set is_disruption to false if ANY apply):
        1. GEOGRAPHY: The disruption is outside Bengaluru.
        2. PAST OR RESOLVED: The text indicates the incident is over, using past tense or resolution words (e.g., "services restored", "resumed", "was delayed", "evacuated", "cleared", "rectified").
        3. POST-MORTEM OR ANALYSIS: The text is discussing the aftermath, audits, reviews, or opinions regarding a previous disruption (e.g., "trigger calls for audit", "exposes fault lines").
        4. CHRONIC ISSUES: General complaints about long-standing infrastructural decay (e.g., garbage piles, stench, broken footpaths, potholes, daily traffic). Reject unless a specific, sudden accident has completely blocked the infrastructure today.
        5. ACCIDENTS & TRAGEDIES: Standard road accidents, localized fires, or fatal incidents (e.g., workers injured, bus accidents) are NOT disruptions UNLESS the text explicitly states they cause massive, persistent traffic halts or require recovery (e.g., cranes removing a 16-wheeler).
        6. ADMINISTRATIVE & POLITICAL: General complaints about infrastructure (e.g., politicians talking about potholes), civic administrative news, or delays in future construction approvals (e.g., "no new metro lines") are NOT active physical disruptions.
        7. ORGANIZED PROTESTS: Protests, rallies, and strikes are NOT disruptions UNLESS the text explicitly states they are actively blocking roads, highways, or public transit. Assume protests are in designated enclosures otherwise.

        Strict Rules for ACCEPTANCE (Set is_disruption to true):
        1. The event is an explicitly announced public service halt (e.g., scheduled BWSSB water cut, BESCOM power outage, BMTC strike) by civic bodies.
        2. The event is happening RIGHT NOW or is scheduled for the FUTURE (e.g., "Metro services suspended", "power cut tomorrow").

        Allowed categories are exactly: "Traffic", "Power", "Water", "Weather", "Infrastructure", "Public Transport", "Others", "Update"
        You must respond strictly in JSON format matching this exact schema:
        Note: The confidence_score must be a floating point number between 0.0 and 1.0 indicating your certainty.
        {{
        "is_disruption": true or false,
        "category": "Traffic",
        "confidence_score": 0.85,
        "reasoning": "A one sentence explanation of your decision or reasoning."
        }}
"""
# Using double curly braces becasue we want python to treat them as literal text instead of trying to evaluate them as code blocks.

def get_disruption_context(headline, description):
    """
    Evaluates news text. Tries Groq (GPT OSS 20B) first, falls back to Google (Gemini) if Groq fails.
    """
    # ----- PRIMARY: GROQ (GPT OSS 20B) -----
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Headline: {headline}\nDescription: {description}"}
            ],
            model="openai/gpt-oss-20b",
            response_format={"type": "json_object"},
            temperature=0                                   # Ensures the model gives a logical output rather than a creative one.
        )

        groq_result = json.loads(chat_completion.choices[0].message.content)
        
        # Extracting data to use in our print statements
        confidence = groq_result.get("confidence_score", 0.0)                   # The 0.0 default ensures that if the model's response doesn't include a confidence score, it will be treated as 0 confidence but will not crash the program due to a missing key.
        reasoning = groq_result.get("reasoning", "No reasoning provided.")
        is_disrupt = groq_result.get("is_disruption")                           #Save the result so we can evalulate confidence score.
        
        # Check if the model is uncertain about its decision
        if confidence < 0.8:
            reasoning = groq_result.get("reasoning", "No reasoning provided.")
            print(f"\nLOW CONFIDENCE from Groq:\n"
                  f"Confidence: {confidence}\n"
                  f"is_disruption: {groq_result.get('is_disruption')}\n"
                  f"Reasoning: {reasoning}\n"
                  f"Routing to Gemini for review...")
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