import os
import json
import base64
from google import genai
from google.genai import types

# Using Gemini API for AI verification
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def verify_safety_kit_photo(base64_image):
    """Verify safety kit distribution using AI"""
    if not client:
        return {"verified": False, "error": "Gemini API key not configured"}

    try:
        prompt = """You are a safety compliance expert. Analyze this image to verify if it shows a waste worker receiving safety equipment (gloves, masks, protective clothing, etc.). 

Respond with JSON format: {'verified': boolean, 'confidence': float, 'items_detected': list, 'concerns': list}

Please verify if this image shows proper safety kit distribution to a waste worker. Check for safety equipment and proper handling."""

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Part.from_bytes(
                    data=base64.b64decode(base64_image),
                    mime_type="image/jpeg",
                ),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        if response.text:
            result = json.loads(response.text)
            return result
        else:
            return {"verified": False, "error": "Empty response from Gemini"}

    except Exception as e:
        return {"verified": False, "error": f"AI verification failed: {str(e)}"}


def verify_waste_segregation(base64_image):
    """Verify waste segregation quality using AI"""
    if not client:
        return {"quality": "unknown", "error": "Gemini API key not configured"}

    try:
        prompt = """You are a waste management expert. Analyze this image to assess waste segregation quality. Check if organic, recyclable, and non-recyclable waste are properly separated. 

Respond with JSON format: {'quality': 'good'|'poor'|'average', 'confidence': float, 'issues': list, 'recommendations': list}

Please assess the waste segregation quality in this image. Look for proper separation of different waste types."""

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Part.from_bytes(
                    data=base64.b64decode(base64_image),
                    mime_type="image/jpeg",
                ),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        if response.text:
            result = json.loads(response.text)
            return result
        else:
            return {"quality": "unknown", "error": "Empty response from Gemini"}

    except Exception as e:
        return {"quality": "unknown", "error": f"AI verification failed: {str(e)}"}


def analyze_community_report_image(base64_image):
    """Analyze community reported waste images"""
    if not client:
        return {"valid": False, "error": "Gemini API key not configured"}

    try:
        prompt = """You are an environmental compliance officer. Analyze this image to determine if it shows legitimate waste management issues that require attention. 

Respond with JSON format: {'valid': boolean, 'severity': 'low'|'medium'|'high', 'waste_type': string, 'description': string, 'action_required': boolean}

Please analyze this community-reported waste image and determine if it represents a valid environmental concern."""

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Part.from_bytes(
                    data=base64.b64decode(base64_image),
                    mime_type="image/jpeg",
                ),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        if response.text:
            result = json.loads(response.text)
            return result
        else:
            return {"valid": False, "error": "Empty response from Gemini"}

    except Exception as e:
        return {"valid": False, "error": f"AI verification failed: {str(e)}"}


def verify_treatment_plant_delivery(base64_image):
    """Verify treatment plant waste delivery"""
    if not client:
        return {"verified": False, "error": "Gemini API key not configured"}

    try:
        prompt = """You are a waste treatment facility inspector. Analyze this image to verify proper waste delivery and segregation at the treatment plant. 

Respond with JSON format: {'verified': boolean, 'segregation_quality': 'good'|'poor'|'average', 'vehicle_compliance': boolean, 'notes': string}

Please verify this waste delivery at the treatment plant. Check for proper segregation and compliance."""

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Part.from_bytes(
                    data=base64.b64decode(base64_image),
                    mime_type="image/jpeg",
                ),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        if response.text:
            result = json.loads(response.text)
            return result
        else:
            return {"verified": False, "error": "Empty response from Gemini"}

    except Exception as e:
        return {"verified": False, "error": f"AI verification failed: {str(e)}"}
