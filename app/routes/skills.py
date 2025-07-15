from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Skill
from app.forms import SkillForm

skills_bp = Blueprint('skills', __name__)

@skills_bp.route('/skills', methods=['GET', 'POST'])
@login_required
def skills():
    error = None
    edit_skill = None
    form = SkillForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = (form.name.data or '').strip()
            category = (form.category.data or '').strip()
            rating = form.rating.data
            skill_id = request.args.get('edit')
            if skill_id:
                # Update
                skill = Skill.query.filter_by(id=skill_id, user_id=current_user.id).first()
                if skill:
                    skill.name = name
                    skill.category = category
                    skill.rating = rating
                    db.session.commit()
                    flash('Skill updated.', 'success')
                    return redirect(url_for('skills.skills'))
                else:
                    error = 'Skill not found.'
            else:
                # Add
                skill = Skill(user_id=current_user.id, name=name, category=category, rating=rating)
                db.session.add(skill)
                db.session.commit()
                flash('Skill added.', 'success')
                return redirect(url_for('skills.skills'))
        else:
            error = 'Please correct the errors in the form.'
    # Edit mode
    edit_id = request.args.get('edit')
    if edit_id:
        edit_skill = Skill.query.filter_by(id=edit_id, user_id=current_user.id).first()
    skills = Skill.query.filter_by(user_id=current_user.id).order_by(Skill.name).all()
    return render_template('skills.html', skills=skills, edit_skill=edit_skill, error=error, form=form)

@skills_bp.route('/skills/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill(skill_id):
    skill = Skill.query.filter_by(id=skill_id, user_id=current_user.id).first_or_404()
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted.', 'success')
    return redirect(url_for('skills.skills')) 