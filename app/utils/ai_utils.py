import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
TOGETHER_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"


def together_ai_request(messages, temperature=0.7, max_tokens=512):
    url = TOGETHER_API_URL
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": TOGETHER_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"{response.status_code} {response.text} for url: {url}"
    except Exception as e:
        return None, str(e)


def analyze_resume(text):
    prompt = (
        "You are a resume expert. Analyze the following resume text and suggest improvements, missing keywords, and any weaknesses. "
        "Return your feedback as a bullet list.\n\nResume:\n" + text
    )
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    result, error = together_ai_request(messages)
    if result:
        feedback = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        return {'feedback': feedback}
    else:
        return {'error': error}


def match_job_roles(input_text):
    import re
    import json
    prompt = f"""
Based on the following skills or resume content, suggest 5–7 relevant job roles.
For each job role, return the response in the following JSON format:

[
  {{
    "job_title": "Job Title",
    "skills": ["Skill1", "Skill2", "Skill3"],
    "certifications": ["Cert1", "Cert2"]
  }},
  ...
]

Only return a valid JSON array. Do not include explanations or extra text.

Input:
{input_text}
"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    result, error = together_ai_request(messages)
    if result:
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        try:
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                roles = json.loads(match.group())
            else:
                roles = json.loads(content)
        except Exception:
            # fallback: parse as list of strings
            roles = [line.strip('- ').strip() for line in content.split('\n') if line.strip().startswith('-')]
        # Normalize: if roles is a list of strings, convert to list of dicts with all keys
        if roles and isinstance(roles[0], str):
            roles = [{"job_title": r, "skills": None, "certifications": None} for r in roles]
        return {"roles": roles}
    else:
        return {"error": error}


def generate_interview_questions(input_text):
    prompt = f"""
You are an expert interviewer.
Given the following user profile (resume, job description, or skills), generate 3-5 behavioral and technical interview questions suitable for this candidate. Return as a JSON list of questions.

User Input:
{input_text}
"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    result, error = together_ai_request(messages)
    if result:
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        import json
        try:
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                json_str = content[start:end]
                questions = json.loads(json_str)
                return {'questions': questions}
            else:
                return {'error': 'Could not parse questions from AI response.'}
        except Exception as e:
            return {'error': f'Error parsing AI response: {e}\nRaw: {content}'}
    else:
        return {'error': error} 