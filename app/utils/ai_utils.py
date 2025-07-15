import os
import requests

def try_openrouter_endpoints(data, headers):
    endpoints = [
        'https://openrouter.ai/v1/chat/completions',
        'https://openrouter.ai/api/v1/chat/completions',
    ]
    last_error = None
    for url in endpoints:
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json(), None
            else:
                last_error = f"{response.status_code} {response.text} for url: {url}"
        except Exception as e:
            last_error = str(e)
    return None, last_error

def analyze_resume(text):
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        return {'error': 'OpenRouter API key not set.'}
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    prompt = (
        "You are a resume expert. Analyze the following resume text and suggest improvements, missing keywords, and any weaknesses. "
        "Return your feedback as a bullet list.\n\nResume:\n" + text
    )
    data = {
        "model": "anthropic/claude-instant-1.1",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    result, error = try_openrouter_endpoints(data, headers)
    if result:
        feedback = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        return {'feedback': feedback}
    else:
        return {'error': error}

def match_job_roles(input_text):
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        return {'error': 'OpenRouter API key not set.'}
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    prompt = f"""
You are an expert career advisor.

Based on the following user input (skills or resume content), suggest 3–5 suitable job roles. For each job role, provide:
1. Job title
2. Required skills
3. Recommended certifications or learning resources

User Input:
{input_text}
"""
    data = {
        "model": "anthropic/claude-instant-1.1",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    result, error = try_openrouter_endpoints(data, headers)
    if result:
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        import json
        try:
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                json_str = content[start:end]
                roles = json.loads(json_str)
                return {'roles': roles}
            else:
                return {'error': 'Could not parse job roles from AI response.'}
        except Exception as e:
            return {'error': f'Error parsing AI response: {e}\nRaw: {content}'}
    else:
        return {'error': error}

def generate_interview_questions(input_text):
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        return {'error': 'OpenRouter API key not set.'}
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    prompt = f"""
You are an expert interviewer.
Given the following user profile (resume, job description, or skills), generate 3-5 behavioral and technical interview questions suitable for this candidate. Return as a JSON list of questions.

User Input:
{input_text}
"""
    data = {
        "model": "anthropic/claude-instant-1.1",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    result, error = try_openrouter_endpoints(data, headers)
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