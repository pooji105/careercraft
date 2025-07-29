import os
import re
import json
import logging
import traceback
import requests
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple, Union

# Model Configuration
TOGETHER_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Simple print-based logging
def log_error(message):
    print(f"[ERROR] {message}")

def log_info(message):
    print(f"[INFO] {message}")

# Load environment variables from .env file
load_dotenv()

# AI Provider Configuration
class AIConfig:
    def __init__(self):
        # Together AI
        self.TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
        self.TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
        self.TOGETHER_MODEL = os.getenv("TOGETHER_MODEL", "mistralai/Mixtral-8x7B-Instruct-v0.1")
        
        # OpenRouter
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        self.OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
        self.OPENROUTER_MODEL = "openai/gpt-3.5-turbo"  # Can be overridden
        
        # Default provider (can be 'together' or 'openrouter')
        self.DEFAULT_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "together").lower()
        
    def get_provider(self, provider: str = None) -> str:
        """Get the provider to use, falling back to default if not specified."""
        provider = (provider or self.DEFAULT_PROVIDER).lower()
        if provider not in ["together", "openrouter"]:
            log_error(f"Invalid provider: {provider}. Defaulting to 'together'.")
            return "together"
        return provider

# Initialize config
ai_config = AIConfig()

def openrouter_request(messages: List[Dict[str, str]], 
                     temperature: float = 0.7, 
                     max_tokens: int = 512,
                     model: str = None) -> Tuple[Optional[dict], Optional[str]]:
    """
    Make a request to the OpenRouter API.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Controls randomness (0.0 to 2.0)
        max_tokens: Maximum number of tokens to generate
        model: Model to use (defaults to OPENROUTER_MODEL)
        
    Returns:
        Tuple of (response_dict, error_message)
    """
    if not ai_config.OPENROUTER_API_KEY:
        return None, "OpenRouter API key not configured"
    
    url = ai_config.OPENROUTER_API_URL
    headers = {
        "Authorization": f"Bearer {ai_config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("APP_URL", "http://localhost:5000"),
        "X-Title": "CareerCraft Interview Simulator"
    }
    
    model = model or ai_config.OPENROUTER_MODEL
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": max(0, min(2.0, temperature)),  # Clamp to valid range
        "max_tokens": max_tokens,
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        error_msg = f"OpenRouter API request failed: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json().get('error', {}).get('message', str(e))
                error_msg = f"OpenRouter API error: {error_detail}"
            except:
                error_msg = f"OpenRouter API error: {e.response.text or str(e)}"
        return None, error_msg


def ai_request(messages: List[Dict[str, str]], 
               temperature: float = 0.7, 
               max_tokens: int = 512,
               provider: str = None) -> Tuple[Optional[dict], Optional[str]]:
    """
    Unified AI request function that routes to the appropriate provider.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Controls randomness (0.0 to 2.0)
        max_tokens: Maximum number of tokens to generate
        provider: AI provider to use ('together' or 'openrouter')
        
    Returns:
        Tuple of (response_dict, error_message)
    """
    provider = ai_config.get_provider(provider)
    
    if provider == "openrouter":
        return openrouter_request(messages, temperature, max_tokens)
    else:  # together
        return together_ai_request(messages, temperature, max_tokens)


def together_ai_request(messages: List[Dict[str, str]], 
                       temperature: float = 0.7, 
                       max_tokens: int = 512) -> Tuple[Optional[dict], Optional[str]]:
    """
    Make a request to the Together AI API.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Controls randomness (0.0 to 1.0)
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        Tuple of (response_dict, error_message)
    """
    if not ai_config.TOGETHER_API_KEY:
        return None, "Together API key not configured"
    
    try:
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {ai_config.TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": TOGETHER_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json(), None
        return None, f"{response.status_code} {response.text}"
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
    result, error = ai_request(messages)
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
    result, error = ai_request(messages)
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


import random

def generate_interview_questions(input_text):
    # Generate 3-5 questions as specified
    num_questions = random.randint(3, 5)
    
    prompt = f"""
You are an expert interviewer. Given the following user profile (resume, job description, or skills), 
generate exactly {num_questions} relevant interview questions. 

Include a mix of:
1. Technical questions specific to the skills mentioned
2. Behavioral questions
3. Situational questions
4. Problem-solving scenarios

Format the response as a JSON array of strings. Example:
["Question 1?", "Question 2?", ...]

User Input:
{input_text}
"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant that generates interview questions."},
        {"role": "user", "content": prompt}
    ]
    
    result, error = ai_request(messages, temperature=0.8, max_tokens=1024, provider="together")
    
    if result:
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        import json
        import re
        try:
            # Extract JSON array from the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                questions = json.loads(json_str)
                # Ensure we have the right number of questions
                if len(questions) > num_questions:
                    questions = questions[:num_questions]
                return questions
            else:
                # Fallback: Try to parse as is
                questions = json.loads(content)
                if isinstance(questions, list):
                    return questions[:num_questions] if len(questions) > num_questions else questions
                return questions
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract questions using regex
            questions = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|$)', content, re.DOTALL)
            if questions:
                return questions[:num_questions] if len(questions) > num_questions else questions
            return ["Error: Could not parse questions from the AI response."]
        except Exception as e:
            return [f"Error generating questions: {str(e)}"]
    else:
        return [f"Error: {error}" if error else "Failed to generate questions"]


def evaluate_interview_answers(questions: List[str], 
                             answers: List[str],
                             provider: str = None) -> List[Dict[str, str]]:
    """
    Evaluate interview answers using AI.
    
    Args:
        questions: List of questions that were asked
        answers: List of corresponding user answers
        provider: AI provider to use ('together' or 'openrouter')
        
    Returns:
        List of dicts with evaluation for each answer
    """
    evaluations = []
    
    for i, (question, answer) in enumerate(zip(questions, answers)):
        system_prompt = """You are an AI assistant."""
        
        user_prompt = f"""
You are an AI interview coach.

Evaluate the following interview question and answer:

Question: {question}
Answer: {answer}

Your task:
1. Tell whether the answer is correct, partially correct, or incorrect.
2. Explain why.
3. Suggest **specific improvements**, even for correct answers.
4. If the answer is weak or incorrect, provide a **model answer**.

IMPORTANT: Respond ONLY with valid JSON. Do not include any text before or after the JSON. Use proper JSON formatting with double quotes and no HTML entities.

Respond in this exact JSON format:
{{
  "verdict": "Correct",
  "feedback": "Your feedback here",
  "model_answer": "Model answer here if needed"
}}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Use the new AI provider system
            result, error = ai_request(
                messages, 
                temperature=0.7, 
                max_tokens=512,
                provider="together"
            )
            
            if result:
                try:
                    # Handle different response formats from different providers
                    if 'choices' in result:  # OpenRouter/Together AI format
                        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    elif 'output' in result:  # Some providers might use 'output'
                        content = result.get('output', '')
                    else:  # Direct response
                        content = json.dumps(result)
                    
                    # Clean up the response to extract JSON
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        
                        # Clean up common JSON issues
                        json_str = json_str.replace('&quot;', '"')  # Fix HTML entities
                        json_str = json_str.replace('&amp;', '&')   # Fix HTML entities
                        json_str = json_str.replace('&lt;', '<')    # Fix HTML entities
                        json_str = json_str.replace('&gt;', '>')    # Fix HTML entities
                        
                        # Remove invalid control characters
                        json_str = ''.join(char for char in json_str if ord(char) >= 32 or char in '\n\r\t')
                        
                        # Fix common escape sequence issues
                        json_str = json_str.replace('\\"', '"')  # Fix double escaped quotes
                        json_str = json_str.replace('\\\\', '\\')  # Fix double escaped backslashes
                        
                        try:
                            evaluation = json.loads(json_str)
                        except json.JSONDecodeError as json_error:
                            # If still fails, try to fix the JSON structure
                            log_error(f"JSON decode error after cleaning: {json_error}")
                            log_error(f"Cleaned JSON: {json_str[:500]}...")
                            
                            # Fallback: create a basic evaluation
                            evaluation = {
                                'verdict': 'Partially Correct',
                                'feedback': 'The AI evaluation encountered a technical issue. Please review your answer and consider providing more specific details.',
                                'model_answer': ''
                            }
                        
                        # Handle model_answer properly - it might be a string or dict
                        model_answer = evaluation.get('model_answer', '')
                        if isinstance(model_answer, dict):
                            model_answer = json.dumps(model_answer)
                        elif isinstance(model_answer, str):
                            model_answer = model_answer.strip()
                        else:
                            model_answer = str(model_answer)
                        
                        # Normalize verdict to title case for consistency
                        verdict = evaluation.get('verdict', 'Incomplete')
                        if verdict.lower() == 'partially correct':
                            verdict = 'Partially Correct'
                        elif verdict.lower() == 'correct':
                            verdict = 'Correct'
                        elif verdict.lower() == 'incorrect':
                            verdict = 'Incorrect'
                        else:
                            verdict = verdict.capitalize()
                        
                        evaluations.append({
                            'question': question,
                            'answer': answer,
                            'verdict': verdict,
                            'feedback': evaluation.get('feedback', 'No feedback provided.').strip(),
                            'model_answer': model_answer if evaluation.get('verdict', '').lower() != 'correct' else ''
                        })
                        log_info(f"Successfully evaluated answer {i+1}/{len(questions)}")
                    else:
                        # If no JSON found, create a fallback evaluation
                        log_error(f"Could not parse JSON from AI response. Content: {content[:200]}...")
                        evaluation = {
                            'verdict': 'Partially Correct',
                            'feedback': 'The AI evaluation encountered a technical issue. Please review your answer and consider providing more specific details.',
                            'model_answer': ''
                        }
                        
                except Exception as e:
                    log_error(f"Error parsing AI response: {str(e)}")
                    log_error(f"Content: {content[:500] if 'content' in locals() else 'No content'}")
                    log_error(traceback.format_exc())
                    evaluations.append({
                        'question': question,
                        'answer': answer,
                        'verdict': 'Error',
                        'feedback': 'Error processing the evaluation. The AI service returned an unexpected response format.',
                        'model_answer': ''
                    })
            else:
                error_msg = error or "No response from AI service"
                log_error(f"AI API Error: {error_msg}")
                raise Exception(f"AI service error: {error_msg}")
                
        except Exception as e:
            log_error(f"Error in evaluate_interview_answers: {str(e)}")
            log_error(traceback.format_exc())
            evaluations.append({
                'question': question,
                'answer': answer,
                'verdict': 'Error',
                'feedback': 'The AI evaluation service is currently unavailable. Please try again later.',
                'model_answer': ''
            })
    
    return evaluations