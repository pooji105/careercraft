from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, make_response, session
from flask_login import login_required, current_user
from app import db
from app.models import Resume, UserPersonalInfo, UserEducation, UserExperience, UserProjects, UserSkills
import json
import io
from datetime import datetime
from app.utils.file_utils import html_to_pdf
from app.utils.helpers import clean_resume_data
from xhtml2pdf import pisa
from werkzeug.utils import secure_filename
from app.models import ResumeAnalyzer
from app.utils.ai_utils import analyze_resume
import tempfile
from app.models import JobMatch, JobMatchHistory, JobMatchResult
from app.utils.file_utils import export_job_match_history_txt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

resume_bp = Blueprint('resume', __name__)

def save_personal_info(user_id, personal_data):
    """Save or update personal information"""
    try:
        # Check if personal info already exists
        personal_info = UserPersonalInfo.query.filter_by(user_id=user_id).first()
        
        if personal_info:
            # Update existing
            personal_info.full_name = personal_data.get('fullName', '')
            personal_info.email = personal_data.get('email', '')
            personal_info.phone = personal_data.get('phone', '')
            personal_info.summary = personal_data.get('summary', '')
            personal_info.linkedin_display = personal_data.get('linkedin', '')
            personal_info.github_display = personal_data.get('github', '')
            personal_info.updated_at = datetime.utcnow()
        else:
            # Create new
            personal_info = UserPersonalInfo(
                user_id=user_id,
                full_name=personal_data.get('fullName', ''),
                email=personal_data.get('email', ''),
                phone=personal_data.get('phone', ''),
                summary=personal_data.get('summary', ''),
                linkedin_display=personal_data.get('linkedin', ''),
                github_display=personal_data.get('github', '')
            )
            db.session.add(personal_info)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error saving personal info: {e}")
        return False

def save_education(user_id, education_data):
    """Save or update education information"""
    try:
        # Delete existing education records for this user
        UserEducation.query.filter_by(user_id=user_id).delete()
        
        # Add new education records
        for edu in education_data:
            if edu.get('institution') and edu.get('degree'):
                education = UserEducation(
                    user_id=user_id,
                    institution=edu.get('institution', ''),
                    degree=edu.get('degree', ''),
                    year=edu.get('year', '')
                )
                db.session.add(education)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error saving education: {e}")
        return False

def save_experience(user_id, experience_data):
    """Save or update experience information"""
    try:
        # Delete existing experience records for this user
        UserExperience.query.filter_by(user_id=user_id).delete()
        
        # Add new experience records
        for exp in experience_data:
            if exp.get('title') and exp.get('company'):
                experience = UserExperience(
                    user_id=user_id,
                    title=exp.get('title', ''),
                    company=exp.get('company', ''),
                    duration=exp.get('duration', '')
                )
                db.session.add(experience)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error saving experience: {e}")
        return False

def save_projects(user_id, projects_data):
    """Save or update projects information"""
    try:
        # Delete existing project records for this user
        UserProjects.query.filter_by(user_id=user_id).delete()
        
        # Add new project records
        for proj in projects_data:
            if proj.get('title'):
                project = UserProjects(
                    user_id=user_id,
                    title=proj.get('title', ''),
                    description=proj.get('description', '')
                )
                db.session.add(project)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error saving projects: {e}")
        return False

def save_skills(user_id, skills_data):
    """Save or update skills information"""
    try:
        # Delete existing skill records for this user
        UserSkills.query.filter_by(user_id=user_id).delete()
        
        # Add new skill records
        for skill in skills_data:
            if skill.get('name'):
                user_skill = UserSkills(
                    user_id=user_id,
                    name=skill.get('name', ''),
                    category=skill.get('category', 'General')
                )
                db.session.add(user_skill)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error saving skills: {e}")
        return False

def get_user_resume_data(user_id):
    """Get all resume data for a user from the new models"""
    try:
        personal_info = UserPersonalInfo.query.filter_by(user_id=user_id).first()
        education = UserEducation.query.filter_by(user_id=user_id).all()
        experience = UserExperience.query.filter_by(user_id=user_id).all()
        projects = UserProjects.query.filter_by(user_id=user_id).all()
        skills = UserSkills.query.filter_by(user_id=user_id).all()
        
        return {
            'personal': {
                'fullName': personal_info.full_name if personal_info else '',
                'email': personal_info.email if personal_info else '',
                'phone': personal_info.phone if personal_info else '',
                'summary': personal_info.summary if personal_info else '',
                'linkedin': personal_info.linkedin_display if personal_info else '',
                'github': personal_info.github_display if personal_info else ''
            },
            'education': [
                {
                    'institution': edu.institution,
                    'degree': edu.degree,
                    'year': edu.year
                } for edu in education
            ],
            'experience': [
                {
                    'title': exp.title,
                    'company': exp.company,
                    'duration': exp.duration
                } for exp in experience
            ],
            'projects': [
                {
                    'title': proj.title,
                    'description': proj.description
                } for proj in projects
            ],
            'skills': [
                {
                    'name': skill.name,
                    'category': skill.category
                } for skill in skills
            ]
        }
    except Exception as e:
        print(f"Error getting user resume data: {e}")
        return None

@resume_bp.route('/resume-builder', methods=['GET', 'POST'])
@login_required
def resume_builder():
    if request.method == 'POST':
        # Get the JSON data from the form
        form_data = request.form.get('resume_data')
        print(f"DEBUG: Received form_data: {form_data[:200]}...")  # Debug: Show first 200 chars
        
        if not form_data:
            flash('No data submitted.', 'danger')
            return redirect(url_for('resume.resume_builder'))
        
        try:
            # Parse the JSON data
            raw_data = json.loads(form_data)
            print(f"DEBUG: Parsed raw_data: {raw_data}")  # Debug: Show parsed data
            
            # Save data step-wise to the new models
            success = True
            
            # Save personal information
            if 'personal' in raw_data and raw_data['personal']:
                if not save_personal_info(current_user.id, raw_data['personal']):
                    success = False
            
            # Save education
            if 'education' in raw_data and raw_data['education']:
                if not save_education(current_user.id, raw_data['education']):
                    success = False
            
            # Save experience
            if 'experience' in raw_data and raw_data['experience']:
                if not save_experience(current_user.id, raw_data['experience']):
                    success = False
            
            # Save projects
            if 'projects' in raw_data and raw_data['projects']:
                if not save_projects(current_user.id, raw_data['projects']):
                    success = False
            
            # Save skills
            if 'skills' in raw_data and raw_data['skills']:
                if not save_skills(current_user.id, raw_data['skills']):
                    success = False
            
            if success:
                flash('Resume data saved successfully!', 'success')
            else:
                flash('Some data could not be saved. Please try again.', 'warning')
            
            return redirect(url_for('resume.view_latest_resume'))
            
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")  # Debug: Show JSON error
            flash('Invalid data format submitted.', 'danger')
            return redirect(url_for('resume.resume_builder'))
        except Exception as e:
            print(f"DEBUG: General error: {e}")  # Debug: Show general error
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('resume.resume_builder'))

    # Get existing data for the form
    existing_data = get_user_resume_data(current_user.id)
    return render_template('resume/resume_builder.html', edit_mode=False, existing_data=existing_data)

@resume_bp.route('/resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    data = json.loads(resume.data)
    return render_template('resume/view_resume.html', resume=resume, data=data)

@resume_bp.route('/view-latest-resume', methods=['GET'])
@login_required
def view_latest_resume():
    try:
        # Get resume data from the new models
        parsed_resume = get_user_resume_data(current_user.id)
        
        if parsed_resume:
            print(f"DEBUG: Found resume data from new models: {parsed_resume}")
        else:
            print("DEBUG: No resume data found, using defaults")
            # Provide safe defaults if no resume exists
            parsed_resume = {
                "personal": {"fullName": "", "email": "", "phone": "", "summary": ""},
                "skills": [],
                "education": [],
                "experience": [],
                "projects": []
            }

        print(f"DEBUG: Final parsed_resume for template: {parsed_resume}")
        return render_template('resume/view_latest_resume.html', resume=parsed_resume)
    except Exception as e:
        print(f"DEBUG: Error in view_latest_resume: {e}")  # Debug: Show any errors
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('resume.resume_builder'))

@resume_bp.route('/save-personal-info', methods=['POST'])
@login_required
def save_personal_info_step():
    """Save personal information step"""
    try:
        data = request.get_json()
        if save_personal_info(current_user.id, data):
            return jsonify({'success': True, 'message': 'Personal information saved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save personal information'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@resume_bp.route('/save-education', methods=['POST'])
@login_required
def save_education_step():
    """Save education step"""
    try:
        data = request.get_json()
        if save_education(current_user.id, data):
            return jsonify({'success': True, 'message': 'Education information saved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save education information'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@resume_bp.route('/save-experience', methods=['POST'])
@login_required
def save_experience_step():
    """Save experience step"""
    try:
        data = request.get_json()
        if save_experience(current_user.id, data):
            return jsonify({'success': True, 'message': 'Experience information saved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save experience information'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@resume_bp.route('/save-projects', methods=['POST'])
@login_required
def save_projects_step():
    """Save projects step"""
    try:
        data = request.get_json()
        if save_projects(current_user.id, data):
            return jsonify({'success': True, 'message': 'Projects information saved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save projects information'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@resume_bp.route('/save-skills', methods=['POST'])
@login_required
def save_skills_step():
    """Save skills step"""
    try:
        data = request.get_json()
        if save_skills(current_user.id, data):
            return jsonify({'success': True, 'message': 'Skills information saved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save skills information'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@resume_bp.route('/resume/<int:resume_id>/download')
@login_required
def download_resume_pdf(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    data = json.loads(resume.data)
    html = render_template('resume/pdf_template.html', data=data)
    pdf = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf)
    if pisa_status.err:
        flash('Error generating PDF.', 'danger')
        return redirect(url_for('resume.view_resume', resume_id=resume.id))
    pdf.seek(0)
    return send_file(pdf, as_attachment=True, download_name='resume.pdf', mimetype='application/pdf')

@resume_bp.route('/resume/download')
@login_required
def download_latest_resume_pdf():
    # Get resume data from the new models
    data = get_user_resume_data(current_user.id)
    if not data:
        flash('No resume found. Please create one.', 'info')
        return redirect(url_for('resume.resume_builder'))
    
    html = render_template('resume/pdf_template.html', data=data)
    pdf = html_to_pdf(html)
    if not pdf:
        flash('Error generating PDF.', 'danger')
        return redirect(url_for('resume.view_latest_resume'))
    return send_file(pdf, as_attachment=True, download_name='resume.pdf', mimetype='application/pdf')

@resume_bp.route('/templates')
@login_required
def templates():
    return render_template('resume/templates.html')

@resume_bp.route('/resume/edit', methods=['GET', 'POST'])
@login_required
def edit_resume():
    # Get the latest resume for the current user
    resume = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).first()
    if not resume:
        flash('No resume found to edit. Please create one first.', 'info')
        return redirect(url_for('resume.resume_builder'))

    if request.method == 'POST':
        form_data = request.form.get('resume_data')
        if not form_data:
            flash('No data submitted.', 'danger')
            return redirect(url_for('resume.edit_resume'))
        try:
            raw_data = json.loads(form_data)
            cleaned_data = clean_resume_data(raw_data)
            data_json = json.dumps(cleaned_data)
            # Update existing resume
            resume.data_json = data_json
            db.session.commit()
            flash('Resume updated successfully!', 'success')
            return redirect(url_for('resume.view_resume', resume_id=resume.id))
        except Exception:
            flash('Invalid data format.', 'danger')
            return redirect(url_for('resume.edit_resume'))

    # Pre-fill form with existing data
    data = json.loads(resume.data_json)
    return render_template('resume/resume_builder.html', edit_mode=True, existing_data=data)

@resume_bp.route('/resume-analyzer', methods=['GET', 'POST'])
@login_required
def resume_analyzer():
    feedback = None
    error = None
    if request.method == 'POST':
        file = request.files.get('resume_file')
        if not file:
            error = 'No file uploaded.'
        else:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[-1].lower()
            text = ''
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.'+ext) as tmp:
                    file.save(tmp.name)
                    tmp_path = tmp.name
                if ext == 'pdf':
                    if HAS_PYMUPDF:
                        doc = fitz.open(tmp_path)
                        text = "\n".join(page.get_text() for page in doc)
                        doc.close()
                    else:
                        from pdfminer.high_level import extract_text
                        text = extract_text(tmp_path)
                elif ext == 'txt':
                    with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                else:
                    error = 'Unsupported file type.'
            except Exception as e:
                error = f'Error extracting text: {e}'
            finally:
                try:
                    import os
                    os.remove(tmp_path)
                except Exception:
                    pass
            if text and not error:
                ai_result = analyze_resume(text)
                if 'feedback' in ai_result:
                    feedback = ai_result['feedback']
                    # Store in ResumeAnalyzer
                    uploaded = ResumeAnalyzer(user_id=current_user.id, filename=filename, suggestions=feedback)
                    db.session.add(uploaded)
                    db.session.commit()
                else:
                    error = ai_result.get('error', 'Unknown error from AI analysis.')
    # Fetch all past uploads for this user, most recent first
    past_uploads = ResumeAnalyzer.query.filter_by(user_id=current_user.id).order_by(ResumeAnalyzer.created_at.desc()).all()
    return render_template('resume/resume_upload.html', feedback=feedback, error=error, past_uploads=past_uploads)

@resume_bp.route('/download-feedback/<int:upload_id>')
@login_required
def download_feedback(upload_id):
    upload = ResumeAnalyzer.query.get_or_404(upload_id)
    if upload.user_id != current_user.id:
        abort(403)
    
    # Create a text file with the feedback
    feedback_text = f"Resume Analysis Feedback\n"
    feedback_text += f"Date: {upload.created_at.strftime('%Y-%m-%d %H:%M')}\n"
    feedback_text += f"\n=== AI Feedback ===\n{upload.suggestions}"
    
    # Create a file-like object in memory
    mem = io.BytesIO()
    mem.write(feedback_text.encode('utf-8'))
    mem.seek(0)
    
    # Return the file as an attachment
    return send_file(
        mem,
        as_attachment=True,
        download_name=f"resume_feedback_{upload_id}.txt",
        mimetype='text/plain'
    )

@resume_bp.route('/job-matcher', methods=['GET', 'POST'])
@login_required
def job_matcher():
    roles = None
    error = None
    error_message = None
    input_text = ''
    resume_file_name = None
    resume_text = None
    interests_or_skills = None
    
    if request.method == 'POST':
        file = request.files.get('resume_file')
        manual_input = request.form.get('manual_input', '').strip()
        
        if file and file.filename:
            resume_file_name = secure_filename(file.filename)
            ext = resume_file_name.rsplit('.', 1)[-1].lower()
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.'+ext) as tmp:
                    file.save(tmp.name)
                    tmp_path = tmp.name
                if ext == 'pdf':
                    if HAS_PYMUPDF:
                        doc = fitz.open(tmp_path)
                        input_text = "\n".join(page.get_text() for page in doc)
                        doc.close()
                    else:
                        from pdfminer.high_level import extract_text
                        input_text = extract_text(tmp_path)
                elif ext == 'txt':
                    with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                        input_text = f.read()
                else:
                    error = 'Unsupported file type.'
            except Exception as e:
                error = f'Error extracting text: {e}'
            finally:
                try:
                    import os
                    os.remove(tmp_path)
                except Exception:
                    pass
            
            if input_text and not error:
                resume_text = input_text
        elif manual_input:
            input_text = manual_input
            interests_or_skills = manual_input
        else:
            error = 'Please upload a resume or enter your skills/interests.'
            
        if input_text and not error:
            from app.utils.ai_utils import match_job_roles
            ai_result = match_job_roles(input_text)
            if 'roles' in ai_result:
                roles = ai_result['roles']
                # Normalize: if roles is a list of strings, convert to list of dicts with all keys
                if roles and isinstance(roles[0], str):
                    roles = [{'job_title': r, 'skills': None, 'certifications': None} for r in roles]
                
                # Save to JobMatchResult table
                try:
                    job_match_result = JobMatchResult(
                        user_id=current_user.id,
                        resume_file_name=resume_file_name,
                        resume_text=resume_text,
                        interests_or_skills=interests_or_skills,
                        matched_roles=json.dumps(roles)
                    )
                    db.session.add(job_match_result)
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving job match result: {e}")
                    db.session.rollback()
            else:
                error = ai_result.get('error', 'Unknown error from AI analysis.')
                error_message = ai_result.get('raw', None)
    
    # Fetch all past job match results for this user, most recent first
    past_job_match_results = JobMatchResult.query.filter_by(user_id=current_user.id).order_by(JobMatchResult.created_at.desc()).all()
    
    # Parse the JSON data for each result
    parsed_past_results = []
    for result in past_job_match_results:
        try:
            matched_roles = json.loads(result.matched_roles) if result.matched_roles else []
        except json.JSONDecodeError:
            matched_roles = []
        
        parsed_past_results.append({
            'id': result.id,
            'resume_file_name': result.resume_file_name,
            'resume_text': result.resume_text,
            'interests_or_skills': result.interests_or_skills,
            'matched_roles': matched_roles,
            'created_at': result.created_at
        })
    
    return render_template('resume/job_matcher.html', 
                         roles=roles, 
                         error=error, 
                         error_message=error_message, 
                         past_job_match_results=parsed_past_results)

@resume_bp.route('/job-matcher/delete/<int:match_id>', methods=['POST'])
@login_required
def delete_job_match(match_id):
    match = JobMatch.query.get_or_404(match_id)
    if match.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('resume.job_matcher'))
    db.session.delete(match)
    db.session.commit()
    flash('Job match result deleted.', 'success')
    return redirect(url_for('resume.job_matcher'))

@resume_bp.route('/job-matcher/history/delete/<int:history_id>', methods=['POST'])
@login_required
def delete_job_match_history(history_id):
    history = JobMatchHistory.query.get_or_404(history_id)
    if history.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('resume.job_matcher'))
    db.session.delete(history)
    db.session.commit()
    flash('Match history entry deleted.', 'success')
    return redirect(url_for('resume.job_matcher'))

@resume_bp.route('/job-matcher/history/download')
@login_required
def download_job_match_history():
    histories = JobMatchHistory.query.filter_by(user_id=current_user.id).order_by(JobMatchHistory.created_at.desc()).all()
    if not histories:
        flash('No match history to download.', 'info')
        return redirect(url_for('resume.job_matcher'))
    file_data = export_job_match_history_txt(histories)
    from flask import send_file
    return send_file(file_data, as_attachment=True, download_name='job_match_history.txt', mimetype='text/plain')

@resume_bp.route('/job-matcher/history')
@login_required
def job_match_history():
    """Show all past job match results for the currently logged-in user"""
    try:
        # Fetch all job match results for the current user, most recent first
        job_match_results = JobMatchResult.query.filter_by(user_id=current_user.id).order_by(JobMatchResult.created_at.desc()).all()
        
        # Parse the JSON data for each result
        parsed_results = []
        for result in job_match_results:
            try:
                matched_roles = json.loads(result.matched_roles) if result.matched_roles else []
            except json.JSONDecodeError:
                matched_roles = []
            
            parsed_results.append({
                'id': result.id,
                'resume_file_name': result.resume_file_name,
                'resume_text': result.resume_text[:200] + '...' if result.resume_text and len(result.resume_text) > 200 else result.resume_text,
                'interests_or_skills': result.interests_or_skills,
                'matched_roles': matched_roles,
                'created_at': result.created_at
            })
        
        return render_template('resume/job_match_history.html', job_match_results=parsed_results)
    except Exception as e:
        flash(f'Error loading job match history: {str(e)}', 'danger')
        return redirect(url_for('resume.job_matcher'))

@resume_bp.route('/job-matcher/history/delete/<int:result_id>', methods=['POST'])
@login_required
def delete_job_match_result(result_id):
    """Delete a specific job match result"""
    try:
        result = JobMatchResult.query.get_or_404(result_id)
        if result.user_id != current_user.id:
            flash('Unauthorized action.', 'danger')
            return redirect(url_for('resume.job_match_history'))
        
        db.session.delete(result)
        db.session.commit()
        flash('Job match result deleted successfully.', 'success')
        return redirect(url_for('resume.job_match_history'))
    except Exception as e:
        flash(f'Error deleting job match result: {str(e)}', 'danger')
        return redirect(url_for('resume.job_match_history'))

@resume_bp.route('/download-matched-roles', methods=['POST'])
def download_matched_roles():
    from flask import send_file, request
    import io, json
    roles = request.form.get("roles")
    roles_list = json.loads(roles)

    output = io.StringIO()
    for role in roles_list:
        output.write(f"Job Title: {role.get('job_title')}\n")
        if role.get("skills"):
            output.write(f"Skills: {', '.join(role['skills'])}\n")
        if role.get("certifications"):
            output.write(f"Certifications: {', '.join(role['certifications'])}\n")
        output.write("\n")

    buffer = io.BytesIO()
    buffer.write(output.getvalue().encode())
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="job_suggestions.txt",
        mimetype="text/plain"
    )

@resume_bp.route('/download-resume', methods=['GET'])
@login_required
def download_resume():
    try:
        # Get resume data from the new models
        data = get_user_resume_data(current_user.id)
        if not data:
            flash('No resume found.', 'warning')
            return redirect(url_for('resume.resume_builder'))

        # Generate PDF
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        pdf.setTitle("Resume")
        pdf.drawString(100, 750, "Resume")
        pdf.drawString(100, 730, f"Full Name: {data.get('personal', {}).get('fullName', 'N/A')}")
        pdf.drawString(100, 710, f"Email: {data.get('personal', {}).get('email', 'N/A')}")
        pdf.drawString(100, 690, f"Phone: {data.get('personal', {}).get('phone', 'N/A')}")
        pdf.drawString(100, 670, f"Summary: {data.get('personal', {}).get('summary', 'N/A')}")
        pdf.drawString(100, 650, "Education:")
        y = 630
        for edu in data.get('education', []):
            pdf.drawString(100, y, f"{edu.get('institution', 'N/A')} - {edu.get('degree', 'N/A')} ({edu.get('year', 'N/A')})")
            y -= 20
        pdf.drawString(100, y, "Experience:")
        y -= 20
        for exp in data.get('experience', []):
            pdf.drawString(100, y, f"{exp.get('title', 'N/A')} at {exp.get('company', 'N/A')} ({exp.get('duration', 'N/A')})")
            y -= 20
        pdf.drawString(100, y, "Projects:")
        y -= 20
        for proj in data.get('projects', []):
            pdf.drawString(100, y, f"{proj.get('title', 'N/A')}: {proj.get('description', 'N/A')}")
            y -= 20
        pdf.drawString(100, y, "Skills:")
        y -= 20
        for skill in data.get('skills', []):
            pdf.drawString(100, y, skill)
            y -= 20
        pdf.save()

        # Return PDF as response
        pdf_buffer.seek(0)
        response = make_response(pdf_buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=resume.pdf'
        return response
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('resume.resume_builder'))