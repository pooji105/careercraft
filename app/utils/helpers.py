import os
from datetime import datetime
import re

def get_openrouter_api_key():
    """Get the OpenRouter API key from environment variables."""
    return os.getenv('OPENROUTER_API_KEY')

def format_date(date_obj):
    """Format a date object to a readable string."""
    if date_obj:
        return date_obj.strftime('%B %d, %Y')
    return ''

def get_file_extension(filename):
    """Get the file extension from a filename."""
    if filename:
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ''

def clean_resume_data(data):
    """
    Clean up resume data dict:
    - Remove duplicate URLs from experience/projects
    - Trim empty entries or sections with no data
    - Sanitize inputs to remove repeated characters (e.g., 'Hhhhhhhhhhh') unless it looks like a valid word
    - For fields like links or descriptions, only keep the first instance if repeated
    """
    def sanitize_text(text, preserve_newlines=False):
        if not isinstance(text, str):
            return text
        # Remove repeated characters (3+ in a row, unless it's a valid word)
        # e.g., 'Hhhhhhhhhhh' -> 'Hhh'
        if preserve_newlines:
            # For summary field, be more lenient - only remove very obvious repeated characters
            # Don't sanitize if the text looks like legitimate content
            if len(text.strip()) > 10 and not re.search(r'(\w)\1{5,}', text):
                return text.strip()
            else:
                return re.sub(r'(\w)\1{2,}', r'\1\1', text.strip())
        else:
            return re.sub(r'(\w)\1{2,}', r'\1\1', text.strip())

    def clean_section(section, unique_fields=None, only_first_fields=None):
        if not isinstance(section, list):
            return []
        seen = set()
        cleaned = []
        for entry in section:
            if not isinstance(entry, dict):
                continue
            # Remove empty entries
            if not any(v for v in entry.values() if v and str(v).strip()):
                continue
            new_entry = {}
            for k, v in entry.items():
                if isinstance(v, str):
                    v = sanitize_text(v.strip())
                if unique_fields and k in unique_fields:
                    if v in seen:
                        continue
                    seen.add(v)
                if only_first_fields and k in only_first_fields:
                    if v in seen:
                        continue
                    seen.add(v)
                new_entry[k] = v
            # Remove empty fields
            new_entry = {k: v for k, v in new_entry.items() if v and str(v).strip()}
            if new_entry:
                cleaned.append(new_entry)
        return cleaned

    cleaned = {}
    # Clean personal info
    if 'personal' in data:
        cleaned['personal'] = {}
        for k, v in data['personal'].items():
            if v and str(v).strip():
                if isinstance(v, str):
                    if k == 'summary':
                        # Preserve newlines in summary field
                        cleaned['personal'][k] = sanitize_text(v.strip(), preserve_newlines=True)
                    else:
                        cleaned['personal'][k] = sanitize_text(v.strip())
                else:
                    cleaned['personal'][k] = v
    # Clean education
    if 'education' in data:
        cleaned['education'] = clean_section(data['education'])
    # Clean experience (remove duplicate company+role, sanitize, remove empty)
    if 'experience' in data:
        # Optionally, could use company+role as unique key
        seen_exp = set()
        cleaned_exp = []
        for entry in data['experience']:
            if not isinstance(entry, dict):
                continue
            key = (entry.get('company', '').strip(), entry.get('role', '').strip())
            if key in seen_exp or not any(v for v in entry.values() if v and str(v).strip()):
                continue
            seen_exp.add(key)
            new_entry = {k: sanitize_text(v.strip()) if isinstance(v, str) else v for k, v in entry.items() if v and str(v).strip()}
            cleaned_exp.append(new_entry)
        cleaned['experience'] = cleaned_exp
    # Clean projects (remove duplicate title, sanitize, remove empty)
    if 'projects' in data:
        seen_proj = set()
        cleaned_proj = []
        for entry in data['projects']:
            if not isinstance(entry, dict):
                continue
            key = entry.get('title', '').strip()
            if key in seen_proj or not any(v for v in entry.values() if v and str(v).strip()):
                continue
            seen_proj.add(key)
            new_entry = {k: sanitize_text(v.strip()) if isinstance(v, str) else v for k, v in entry.items() if v and str(v).strip()}
            cleaned_proj.append(new_entry)
        cleaned['projects'] = cleaned_proj
    # Clean skills (remove duplicate name, sanitize, remove empty)
    if 'skills' in data:
        seen_skill = set()
        cleaned_skill = []
        for entry in data['skills']:
            if not isinstance(entry, dict):
                continue
            key = entry.get('name', '').strip().lower()
            if key in seen_skill or not any(v for v in entry.values() if v and str(v).strip()):
                continue
            seen_skill.add(key)
            new_entry = {k: sanitize_text(v.strip()) if isinstance(v, str) else v for k, v in entry.items() if v and str(v).strip()}
            cleaned_skill.append(new_entry)
        cleaned['skills'] = cleaned_skill
    return cleaned 