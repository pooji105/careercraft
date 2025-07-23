from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
import os
from flask import request, redirect, url_for, flash, send_from_directory, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import JobApplication
import csv
import io

UPLOAD_FOLDER = os.path.join('instance', 'job_uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/job-tracker', methods=['GET', 'POST'])
@login_required
def job_tracker():
    try:
        error = None
        edit_job = None
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        # Handle filter and search
        filter_status = request.args.get('status', '').strip()
        search = request.args.get('search', '').strip()
        if request.method == 'POST':
            company = request.form.get('company', '').strip()
            role = request.form.get('role', '').strip()
            status = request.form.get('status', '').strip()
            notes = request.form.get('notes', '').strip()
            job_id = request.args.get('edit')
            file = request.files.get('jd_file')
            filename = None
            if file and file.filename:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                else:
                    error = 'Only PDF or TXT files are allowed for job description.'
            if not company or not role or not status:
                error = 'Company, role, and status are required.'
            if not error:
                if job_id:
                    # Update
                    job = JobApplication.query.filter_by(id=job_id, user_id=current_user.id).first()
                    if job:
                        job.company = company
                        job.role = role
                        job.status = status
                        job.notes = notes
                        if filename:
                            job.jd_file = filename
                        db.session.commit()
                        flash('Job application updated.', 'success')
                        return redirect(url_for('jobs.job_tracker'))
                    else:
                        error = 'Job application not found.'
                else:
                    # Add
                    job = JobApplication(user_id=current_user.id, company=company, role=role, status=status, notes=notes, jd_file=filename)
                    db.session.add(job)
                    db.session.commit()
                    flash('Job application added.', 'success')
                    return redirect(url_for('jobs.job_tracker'))
        # Edit mode
        edit_id = request.args.get('edit')
        if edit_id:
            edit_job = JobApplication.query.filter_by(id=edit_id, user_id=current_user.id).first()
        # Filtering and searching
        jobs_query = JobApplication.query.filter_by(user_id=current_user.id)
        if filter_status:
            jobs_query = jobs_query.filter_by(status=filter_status)
        if search:
            jobs_query = jobs_query.filter(
                (JobApplication.company.ilike(f'%{search}%')) |
                (JobApplication.role.ilike(f'%{search}%'))
            )
        jobs = jobs_query.order_by(JobApplication.created_at.desc()).all()
        statuses = ['applied', 'interview', 'offer']
        current_app.logger.info('Rendering job tracker template')
        return render_template('jobs/tracker.html', jobs=jobs, edit_job=edit_job, error=error, statuses=statuses, filter_status=filter_status, search=search)
    except Exception as e:
        current_app.logger.error(f'Error in job_tracker: {str(e)}')
        return f'Error: {str(e)}', 500

@jobs_bp.route('/delete/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    job = JobApplication.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    # Optionally delete the file
    if job.jd_file:
        file_path = os.path.join(UPLOAD_FOLDER, job.jd_file)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(job)
    db.session.commit()
    flash('Job application deleted.', 'success')
    return redirect(url_for('jobs.job_tracker'))

@jobs_bp.route('/download/<int:job_id>')
@login_required
def download_jd(job_id):
    job = JobApplication.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    if not job.jd_file:
        flash('No job description file found.', 'danger')
        return redirect(url_for('jobs.job_tracker'))
    return send_from_directory(UPLOAD_FOLDER, job.jd_file, as_attachment=True)

@jobs_bp.route('/download-csv')
@login_required
def download_csv():
    jobs = JobApplication.query.filter_by(user_id=current_user.id).order_by(JobApplication.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Company', 'Role', 'Status', 'Notes', 'Upload Date'])
    for job in jobs:
        writer.writerow([
            job.company,
            job.role,
            job.status,
            job.notes or '',
            job.created_at.strftime('%Y-%m-%d %H:%M') if job.created_at else ''
        ])
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    from flask import send_file
    return send_file(mem, as_attachment=True, download_name='job_applications.csv', mimetype='text/csv')

@jobs_bp.route('/applications')
@login_required
def applications():
    return render_template('jobs/applications.html') 