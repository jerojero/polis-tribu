from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

# from app import db
from app.forms import bp
from app.forms.questionaire import create_questionaire
from wtforms import RadioField, StringField, BooleanField, SubmitField
from app.models import Question, Section


@bp.route('/questionaire/<int:section_id>', methods=['GET', 'POST'])
@bp.route('/questionaire/', methods=['GET', 'POST'])
@login_required
def questionaire(section_id=None):
    if not section_id:
        section_id = current_user.last_question or 1
    section = Section.query.filter_by(id=section_id).first()

    _form = []
    print(_form)

    for question in section.questions.all():
        if question.question_type != "header":
            title = question.title
            answers = question.answer.all()
            choices = [(answer.id, answer.text) for answer in answers]
            _form.append((f"question_{question.id}", RadioField(
                label=title, choices=choices)))

    _form.append(("submit", SubmitField("Siguiente")))

    form = create_questionaire(_form)()

    if form.validate_on_submit():
        next_section = section.id + 1
        return redirect(url_for('forms.questionaire', section_id=next_section))

    return render_template('forms/questionaire.html', section=section, form=form)
