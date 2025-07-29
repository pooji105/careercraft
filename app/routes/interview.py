import os
os.environ['FLASK_ENV'] = 'development'

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, jsonify, abort
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import InterviewFeedback, InterviewResponse, db, User
from app.utils.ai_utils import generate_interview_questions, analyze_resume, evaluate_interview_answers
from app.forms.interview_forms import InterviewQuestionsForm, InterviewAnswersForm
import traceback
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
    form = InterviewQuestionsForm()
    questions = []
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Generate interview questions based on the prompt
            prompt = form.prompt.data
            if prompt and len(prompt.strip()) > 0:
                questions = generate_interview_questions(prompt)
                if not questions:
                    flash('Failed to generate questions. Please try again with more details.', 'warning')
                session['generated_questions'] = questions  # Store in session for reference
        except Exception as e:
            current_app.logger.error(f"Error generating interview questions: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            flash('An error occurred while generating questions. Please try again.', 'error')
    
    # Check for existing evaluated questions from database
    evaluated_questions = []
    if 'last_response_ids' in session:
        try:
            responses = InterviewResponse.query.filter(
                InterviewResponse.id.in_(session['last_response_ids']),
                InterviewResponse.user_id == current_user.id
            ).order_by(InterviewResponse.id).all()
            
            evaluated_questions = [{
                'question': r.question,
                'answer': r.answer,
                'verdict': r.verdict,
                'feedback': r.feedback,
                'model_answer': r.model_answer
            } for r in responses]
            

        except Exception as e:
            current_app.logger.error(f"Error loading evaluated questions: {str(e)}")
    
    # For GET requests or after form processing
    return render_template(
        'interview/simulator.html',
        form=form,
        questions=session.get('generated_questions', []),
        evaluated_questions=evaluated_questions,
        title='Interview Simulator'
    )

@interview_bp.route('/evaluate-answers', methods=['POST'])
@login_required
def evaluate_answers():
    try:
        if 'generated_questions' not in session:
            return jsonify({'error': 'No interview session found. Please generate questions first.'}), 400
        
        questions = session['generated_questions']
        answers = []
        
        # Extract answers from form data
        for i in range(len(questions)):
            answer = request.form.get(f'answer_{i}')
            if answer:
                answers.append(answer)
        
        if len(answers) != len(questions):
            return jsonify({'error': 'Number of answers does not match number of questions.'}), 400
        
        # Evaluate answers using AI and store individual responses
        try:
            evaluations = evaluate_interview_answers(questions, answers)
            
            # Get resume filename from session if available
            resume_filename = session.get('uploaded_resume_filename', None)
            
            # Store each Q&A pair as individual InterviewResponse records
            response_ids = []
            for i in range(len(questions)):
                evaluation = evaluations[i]
                
                response = InterviewResponse(
                    user_id=current_user.id,
                    resume_filename=resume_filename,
                    question=questions[i],
                    answer=answers[i],
                    verdict=evaluation['verdict'],
                    feedback=evaluation['feedback'],
                    model_answer=evaluation.get('model_answer', '')
                )
                db.session.add(response)
                db.session.flush()  # This ensures the ID is generated
                response_ids.append(response.id)
            
            db.session.commit()
            
            # Store response IDs in session for reference
            session['last_response_ids'] = response_ids
            
            print(f"\n=== DEBUG: Interview responses saved successfully (IDs: {response_ids}) ===\n")
            
            # Prepare response with all feedback data
            response_data = {
                'success': True,
                'questions': questions,
                'answers': answers,
                'evaluations': evaluations,
                'response_ids': response_ids
            }
            
            # Return the successful response
            return jsonify(response_data), 200
            
        except Exception as e:
            db.session.rollback()
            print(f"\n=== ERROR: Failed to save feedback ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("\nTraceback:")
            import traceback
            traceback.print_exc()
            print("\n")
            
            return jsonify({
                'success': False,
                'error': f'Failed to save feedback: {str(e)}'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"Error evaluating answers: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'error': 'An error occurred while evaluating your answers. Please try again.'
        }), 500

@interview_bp.route('/interview-simulator/delete/<int:session_id>', methods=['POST'])
@login_required
def delete_session(session_id):
    # Implementation for deleting a session
    pass

@interview_bp.route('/interview/feedback/<int:id>', methods=['GET', 'POST'])
@login_required
def interview_feedback(id):
    """Display interview feedback with PDF download and save options."""
    try:
        # Get feedback record
        feedback = InterviewFeedback.query.get_or_404(id)
        
        # Verify ownership if feedback is user-specific
        if feedback.user_id and feedback.user_id != current_user.id:
            abort(403)  # Forbidden
            
        # Parse JSON fields safely with validation
        questions_data = []
        answers_data = []
        model_answers_data = []
        feedback_data = []
        
        try:
            questions_data = json.loads(feedback.questions_json) if feedback.questions_json else []
            answers_data = json.loads(feedback.answers_json) if feedback.answers_json else []
            model_answers_data = json.loads(feedback.model_answers_json) if feedback.model_answers_json else []
            feedback_data = json.loads(feedback.feedback_json) if feedback.feedback_json else []
            
            # Ensure all are lists
            if not isinstance(questions_data, list) or not isinstance(answers_data, list) or not isinstance(model_answers_data, list) or not isinstance(feedback_data, list):
                raise ValueError("Invalid data format")
                
            # Ensure all lists have the same length
            max_length = max(len(questions_data), len(answers_data), len(model_answers_data), len(feedback_data))
            questions_data = questions_data + [''] * (max_length - len(questions_data))
            answers_data = answers_data + [''] * (max_length - len(answers_data))
            model_answers_data = model_answers_data + [''] * (max_length - len(model_answers_data))
            feedback_data = feedback_data + [''] * (max_length - len(feedback_data))
            
        except (json.JSONDecodeError, ValueError) as e:
            current_app.logger.error(f"Error parsing feedback data: {str(e)}")
            flash('Error loading feedback data. Please try again.', 'error')
            return redirect(url_for('interview.interview_simulator'))

        # Handle PDF generation
        if request.method == "POST" and "download_pdf" in request.form:
            try:
                # Generate PDF with proper error handling
                html = render_template("interview_feedback.html",
                                    questions=questions_data,
                                    answers=answers_data,
                                    model_answers=model_answers_data,
                                    feedback_list=feedback_data)
                
                pdf = BytesIO()
                result = pisa.CreatePDF(
                    BytesIO(html.encode('UTF-8')), 
                    dest=pdf,
                    encoding='UTF-8',
                    link_callback=None
                )
                
                if not result.err:
                    pdf.seek(0)
                    return send_file(
                        pdf,
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name=f'careercraft_feedback_{id}.pdf'
                    )
                else:
                    current_app.logger.error(f"PDF generation error: {result.err}")
                    flash('Failed to generate PDF. Please try again.', 'error')
                    
            except Exception as e:
                current_app.logger.error(f"PDF generation error: {str(e)}")
                flash('An error occurred while generating PDF.', 'error')
                return redirect(url_for('interview.interview_simulator'))

        # Handle save to dashboard
        elif request.method == "POST" and "save_feedback" in request.form:
            try:
                # In a real implementation, you might want to create a dashboard entry here
                flash('Feedback saved to your dashboard successfully!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                current_app.logger.error(f"Error saving to dashboard: {str(e)}")
                flash('Failed to save to dashboard. Please try again.', 'error')

        # For GET requests or if no valid POST action
        return render_template(
            "interview_feedback.html",
            questions=questions_data,
            answers=answers_data,
            model_answers=model_answers_data,
            feedback_list=feedback_data,
            title=f'Interview Feedback - {feedback.created_at.strftime("%B %d, %Y")}'
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in interview_feedback: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('interview.interview_simulator'))

@interview_bp.route('/export-feedback-pdf', methods=['POST'])
@login_required
def export_feedback_pdf():
    try:
        # Get feedback ID from form data or session
        feedback_id = request.form.get('feedback_id')
        if not feedback_id and 'last_feedback_id' in session:
            feedback_id = session['last_feedback_id']
        
        if not feedback_id:
            flash('No feedback data available for PDF generation.', 'error')
            return redirect(url_for('interview.interview_simulator'))
        
        # Get feedback record
        feedback = InterviewFeedback.query.filter(
            InterviewFeedback.id == feedback_id,
            InterviewFeedback.user_id == current_user.id
        ).first()
        
        if not feedback:
            flash('No feedback found for the specified session.', 'error')
            return redirect(url_for('interview.interview_simulator'))
        
        # Prepare data for template
        try:
            questions = json.loads(feedback.questions_json) if feedback.questions_json else []
            answers = json.loads(feedback.answers_json) if feedback.answers_json else []
            model_answers = json.loads(feedback.model_answers_json) if feedback.model_answers_json else []
            evaluations = json.loads(feedback.feedback_json) if feedback.feedback_json else []
            
            # Ensure all lists have the same length
            max_length = max(len(questions), len(answers), len(model_answers), len(evaluations))
            questions = questions + [''] * (max_length - len(questions))
            answers = answers + [''] * (max_length - len(answers))
            model_answers = model_answers + [''] * (max_length - len(model_answers))
            evaluations = evaluations + [{}] * (max_length - len(evaluations))
            
            feedback_data = []
            for i in range(max_length):
                evaluation = evaluations[i] if i < len(evaluations) else {}
                feedback_data.append({
                    'question': questions[i] if i < len(questions) else 'No question available',
                    'answer': answers[i] if i < len(answers) else 'No answer provided',
                    'model_answer': model_answers[i] if i < len(model_answers) else '',
                    'verdict': evaluation.get('verdict', 'No verdict'),
                    'explanation': evaluation.get('explanation', 'No explanation available')
                })
        except json.JSONDecodeError:
            current_app.logger.error(f'Error parsing feedback data for feedback ID {feedback.id}')
            flash('Error parsing feedback data. Please try again.', 'error')
            return redirect(url_for('interview.interview_simulator'))
        
        # Generate PDF
        pdf = html_to_pdf(
            'interview/feedback_pdf.html',
            feedbacks=feedback_data,
            user=current_user,
            date=datetime.utcnow()
        )
        
        if not pdf:
            flash('Failed to generate PDF. Please try again.', 'error')
            return redirect(url_for('interview.interview_simulator'))
        
        # Return PDF as downloadable file
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=interview_feedback.pdf'
        return response
        
    except Exception as e:
        current_app.logger.error(f'Error generating PDF: {str(e)}')
        current_app.logger.error(traceback.format_exc())
        flash('An error occurred while generating the PDF. Please try again.', 'error')
        return redirect(url_for('interview.interview_simulator'))

@interview_bp.route('/export-session-pdf/<int:session_id>')
@login_required
def export_session_pdf(session_id):
    # Implementation for exporting session to PDF
    pass