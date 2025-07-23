from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app import db
from app.models import Resume
import json
import io
from app.utils.file_utils import html_to_pdf
from app.utils.helpers import clean_resume_data
from xhtml2pdf import pisa
from werkzeug.utils import secure_filename
from app.models import UploadedResume
from app.utils.ai_utils import analyze_resume
import tempfile
from app.models import JobMatch, JobMatchHistory
from app.utils.file_utils import export_job_match_history_txt

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/')
@login_required
def resume_builder():
    return render_template('resume/builder.html')

@resume_bp.route('/resume-builder', methods=['GET', 'POST'])
@login_required
def multi_step_resume_builder():
    if request.method == 'POST':
        form_data = request.form.get('resume_data')
        if not form_data:
            flash('No data submitted.', 'danger')
            return redirect(url_for('resume.multi_step_resume_builder'))
        try:
            raw_data = json.loads(form_data)
            cleaned_data = clean_resume_data(raw_data)
            data_json = json.dumps(cleaned_data)
        except Exception:
            flash('Invalid data format.', 'danger')
            return redirect(url_for('resume.multi_step_resume_builder'))
        resume = Resume(user_id=current_user.id, data_json=data_json)
        db.session.add(resume)
        db.session.commit()
        flash('Resume saved successfully!', 'success')
        return redirect(url_for('resume.view_resume', resume_id=resume.id))
    return render_template('resume/resume_builder.html', edit_mode=False, existing_data=None)

@resume_bp.route('/resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    data = json.loads(resume.data_json)
    return render_template('resume/view_resume.html', resume=resume, data=data)

@resume_bp.route('/resume/view')
@login_required
def view_latest_resume():
    resume = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).first()
    if not resume:
        flash('No resume found. Please create one.', 'info')
        return redirect(url_for('resume.multi_step_resume_builder'))
    data = json.loads(resume.data_json)
    return render_template('resume/view_resume.html', resume=resume, data=data)

@resume_bp.route('/resume/<int:resume_id>/download')
@login_required
def download_resume_pdf(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    data = json.loads(resume.data_json)
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
    resume = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).first()
    if not resume:
        flash('No resume found. Please create one.', 'info')
        return redirect(url_for('resume.multi_step_resume_builder'))
    data = json.loads(resume.data_json)
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
        return redirect(url_for('resume.multi_step_resume_builder'))

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
                    # Store in UploadedResume
                    uploaded = UploadedResume(user_id=current_user.id, filename=filename, suggestions=feedback)
                    db.session.add(uploaded)
                    db.session.commit()
                else:
                    error = ai_result.get('error', 'Unknown error from AI analysis.')
    # Fetch all past uploads for this user, most recent first
    past_uploads = UploadedResume.query.filter_by(user_id=current_user.id).order_by(UploadedResume.created_at.desc()).all()
    return render_template('resume/resume_upload.html', feedback=feedback, error=error, past_uploads=past_uploads)

@resume_bp.route('/job-matcher', methods=['GET', 'POST'])
@login_required
def job_matcher():
    roles = None
    error = None
    error_message = None
    input_text = ''
    if request.method == 'POST':
        file = request.files.get('resume_file')
        manual_input = request.form.get('manual_input', '').strip()
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[-1].lower()
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
        elif manual_input:
            input_text = manual_input
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
            else:
                error = ai_result.get('error', 'Unknown error from AI analysis.')
                error_message = ai_result.get('raw', None)
    # Fetch all past job matches for this user, most recent first
    past_matches = JobMatch.query.filter_by(user_id=current_user.id).order_by(JobMatch.created_at.desc()).all()
    raw_histories = JobMatchHistory.query.filter_by(user_id=current_user.id).order_by(JobMatchHistory.created_at.desc()).all()
    import json
    parsed_match_histories = [
        {
            'id': hist.id,
            'created_at': hist.created_at,
            'input_text': hist.input_text,
            'roles': json.loads(hist.matched_roles_json)
        }
        for hist in raw_histories
    ]
    return render_template('resume/job_matcher.html', roles=roles, error=error, error_message=error_message, past_matches=past_matches, match_histories=parsed_match_histories)

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

@resume_bp.route('/download-resume')
@login_required
def download_resume():
    user_data = {
        "name": "Poojitha",
        "email": "poojithasaidurga_marella@srmup.edu.in",
        "phone": "9391028218",
        "linkedin": "linkedin.com/in/poojitha",
        "github": "github.com/pooji105",
        "summary": "Enthusiastic developer with internship experience...",
        "skills": {
            "Programming": ["Python", "C++", "SQL"],
            "Web Dev": ["HTML", "CSS", "Flask"],
            "Tools": ["Figma", "Git", "Postman"]
        },
        "work_experience": [
            {
                "title": "Intern",
                "company": "Edubot",
                "duration": "Jun 2025 – Jul 2025",
                "description": [
                    "Worked on career recommendation engine.",
                    "Integrated OpenRouter API with Flask backend."
                ]
            }
        ],
        "projects": [
            {
                "title": "CareerCraft – Flask",
                "tech": "Flask, PostgreSQL",
                "description": [
                    "Built resume builder and AI job matcher.",
                    "Integrated skill gap analyzer and interview simulator."
                ]
            }
        ],
        "education": [
            {
                "degree": "B.Tech CSE",
                "institution": "SRM University – AP",
                "years": "2022 – 2026",
                "cgpa": "8.3"
            },
            {
                "degree": "Junior College",
                "institution": "Narayana",
                "years": "2020 – 2022",
                "cgpa": "94.9"
            }
        ]
    }

    html = render_template("resume/resume_template.html", **user_data)
    result = io.BytesIO()
    pisa.CreatePDF(html, dest=result)
    result.seek(0)
    return send_file(result, download_name="resume.pdf", as_attachment=True) 