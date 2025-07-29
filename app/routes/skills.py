from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Skill
from app.forms import SkillForm

# Create a blueprint for skills with URL prefix
skills_bp = Blueprint('skills', __name__)

@skills_bp.route('/')
@skills_bp.route('/skill-tracker', methods=['GET', 'POST'])  # Keeping both URLs for backward compatibility
@login_required
def skills():
    """Handle the skill tracker page and form submission."""
    error = None
    edit_skill = None
    form = SkillForm()
    
    try:
        if request.method == 'POST' and form.validate_on_submit():
            name = (form.name.data or '').strip()
            category = (form.category.data or '').strip()
            rating = form.rating.data
            
            # Validate inputs
            if not name:
                raise ValueError("Skill name is required.")
            if not (1 <= rating <= 5):
                raise ValueError("Rating must be between 1 and 5.")
            
            skill_id = request.args.get('edit')
            
            try:
                if skill_id:
                    # Update existing skill
                    skill = Skill.query.filter_by(id=skill_id, user_id=current_user.id).first()
                    if not skill:
                        raise ValueError("Skill not found or you don't have permission to edit it.")
                    
                    skill.name = name
                    skill.category = category
                    skill.rating = rating
                    db.session.commit()
                    flash('Skill updated successfully!', 'success')
                else:
                    # Add new skill
                    skill = Skill(
                        user_id=current_user.id,
                        name=name,
                        category=category,
                        rating=rating
                    )
                    db.session.add(skill)
                    db.session.commit()
                    flash('Skill added successfully!', 'success')
                
                return redirect(url_for('skills.skills'))
                
            except Exception as e:
                db.session.rollback()
                error = f"An error occurred: {str(e)}"
                print(f"Database error: {str(e)}")
        
        elif request.method == 'POST' and not form.validate():
            error = 'Please correct the errors in the form.'
            for field, errors in form.errors.items():
                for error_msg in errors:
                    error = f"{field}: {error_msg}"
                    break
                if error:
                    break
    
    except Exception as e:
        error = f"An unexpected error occurred: {str(e)}"
        print(f"Error in skills route: {str(e)}")
    
    # Handle edit mode
    edit_id = request.args.get('edit')
    if edit_id:
        edit_skill = Skill.query.filter_by(id=edit_id, user_id=current_user.id).first()
        if not edit_skill:
            flash('Skill not found or you do not have permission to edit it.', 'error')
            return redirect(url_for('skills.skills'))
    
    # Get all skills for the current user
    try:
        skills = Skill.query.filter_by(user_id=current_user.id).order_by(Skill.name).all()
    except Exception as e:
        skills = []
        error = "Error loading skills. Please try again later."
        print(f"Error loading skills: {str(e)}")
    
    return render_template(
        'skills.html',
        skills=skills,
        edit_skill=edit_skill,
        error=error,
        form=form
    )

@skills_bp.route('/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill(skill_id):
    """Delete a skill from the database."""
    skill = Skill.query.filter_by(id=skill_id, user_id=current_user.id).first()
    if not skill:
        flash('Skill not found or you do not have permission to delete it.', 'error')
    else:
        try:
            db.session.delete(skill)
            db.session.commit()
            flash('Skill deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting the skill.', 'error')
            # Log the error for debugging
            print(f"Error deleting skill: {str(e)}")
    return redirect(url_for('skills.skills'))