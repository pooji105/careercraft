from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from app import db
from app.models import InterviewFeedback
from app.utils.ai_utils import generate_interview_questions
import json
from flask import render_template as flask_render_template
from app.utils.file_utils import html_to_pdf

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/')
@login_required
def interview_prep():
    return render_template('interview/prep.html')

@interview_bp.route('/practice')
@login_required
def practice():
    return render_template('interview/practice.html')

@interview_bp.route('/interview-simulator', methods=['GET', 'POST'])
@login_required
def interview_simulator():
    questions = None
    feedback = None
    answers = None
    profile_input = None
    error = None
    if request.method == 'POST':
        profile_input = request.form.get('profile_input', '').strip()
        questions_json = request.form.get('questions_json')
        if questions_json:
            # User submitted answers for feedback
            questions = json.loads(questions_json)
            answers = [request.form.get(f'answer_{i}', '') for i in range(len(questions))]
            # Call OpenRouter for feedback
            from app.utils.ai_utils import analyze_resume
            ai_input = '\n'.join([f'Q: {q}\nA: {a}' for q, a in zip(questions, answers)])
            prompt = f"You are an expert interviewer. Give constructive feedback on the following interview answers. For each, provide a short bullet-point critique.\n\n{ai_input}"
            ai_result = analyze_resume(prompt)
            if 'feedback' in ai_result:
                # Split feedback into list if possible
                feedback = [line.strip('-• ') for line in ai_result['feedback'].split('\n') if line.strip()]
                # Store in InterviewFeedback
                feedback_json = json.dumps(feedback)
                db.session.add(InterviewFeedback(user_id=current_user.id, questions_json=questions_json, feedback_json=feedback_json))
                db.session.commit()
            else:
                error = ai_result.get('error', 'Error getting feedback from AI.')
        elif profile_input:
            # Generate questions
            ai_result = generate_interview_questions(profile_input)
            if 'questions' in ai_result:
                questions = ai_result['questions']
            else:
                error = ai_result.get('error', 'Error generating questions from AI.')
    # Fetch all past interview feedback for this user, most recent first
    past_sessions = InterviewFeedback.query.filter_by(user_id=current_user.id).order_by(InterviewFeedback.created_at.desc()).all()
    # Parse questions_json and feedback_json for each session
    for session in past_sessions:
        try:
            session.questions = json.loads(session.questions_json) if session.questions_json else []
        except Exception:
            session.questions = []
        try:
            session.feedback = json.loads(session.feedback_json) if session.feedback_json else []
        except Exception:
            session.feedback = []
    return render_template('interview.html', questions=questions, feedback=feedback, answers=answers, profile_input=profile_input, error=error, past_sessions=past_sessions)

@interview_bp.route('/interview-simulator/delete/<int:session_id>', methods=['POST'])
@login_required
def delete_session(session_id):
    session = InterviewFeedback.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('interview.interview_simulator'))
    db.session.delete(session)
    db.session.commit()
    flash('Interview session deleted.', 'success')
    return redirect(url_for('interview.interview_simulator'))

@interview_bp.route('/interview-simulator/export/<int:session_id>')
@login_required
def export_session_pdf(session_id):
    session = InterviewFeedback.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('interview.interview_simulator'))
    import json
    questions = json.loads(session.questions_json)
    feedback = json.loads(session.feedback_json)
    # For demo, user answers are not stored; show as N/A or blank
    answers = ["N/A"] * len(questions)
    html = flask_render_template('interview_pdf.html', session=session, questions=questions, answers=answers, feedback=feedback)
    pdf = html_to_pdf(html)
    if not pdf:
        flash('Error generating PDF.', 'danger')
        return redirect(url_for('interview.interview_simulator'))
    return send_file(pdf, as_attachment=True, download_name='interview_session.pdf', mimetype='application/pdf') 