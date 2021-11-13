from flask import render_template, redirect, url_for, current_app
from flask_login import login_required, current_user

from app import db
from . import bp
from .forms_forms import create_questionaire, make_question_form
from wtforms import SubmitField
from app.models import Section, Results, Answer, Payment, User


@bp.route('/questionaire/<int:section_id>', methods=['GET', 'POST'])
@bp.route('/questionaire/', methods=['GET', 'POST'])
@login_required
def questionaire(section_id=None):
    if not section_id:
        if current_user.selected:
            # section_id = 25  # This should go live on sunday.
            section_id = 1  # Delete on sunday
        else:
            section_id = 1
    section = Section.query.filter_by(id=section_id).first()

    _form = []
    _form_special = None

    for question in section.questions.all():
        if question.question_type == "hd":
            continue

        elif question.question_type == "fc":
            _form_special = make_question_form(question, current_user)
        elif question.question_type == "fp":
            _form_special = make_question_form(question, current_user)
        else:
            if current_user.doctor:
                if question.id == 3005:
                    continue
            else:
                if question.id == 30015:
                    continue

            _form.append(make_question_form(question, current_user))

    _form.append(("next", SubmitField("Siguiente")))

    if not _form_special:
        form = create_questionaire(_form)()
    else:
        form = _form_special()

    if form.validate_on_submit():
        current_app.logger.info("Validated on submit")
        if form.next.data:
            next_section = section.id + 1
        else:
            next_section = section.id - 1

        for question in section.questions.all():
            last_question = User.query.get(current_user.id).last_question
            if last_question not in [current_app.config['LASTQ_X'], current_app.config['LASTQ_D']]:
                User.query.get(current_user.id).last_question = question.id
                db.session.commit()
            if question.question_type == "hd":
                continue
            elif question.question_type == "fc":
                contact_method = form.contact_method.data
                current_user.contact = contact_method
                db.session.commit()
            elif question.question_type == "fp":
                name = form.name.data
                last_name = form.last_name.data
                rut = form.rut.data
                bank = form.bank.data
                account = form.account.data
                account_number = str(form.account_number.data)
                third_party = form.third_party.data
                r = Payment(first_name=name,
                            last_name=last_name,
                            rut=rut,
                            bank=bank,
                            account=account,
                            account_number=account_number,
                            permission=third_party,
                            user_id=current_user.id)
                db.session.add(r)
                db.session.commit()
            else:
                if current_user.doctor:
                    if question.id == 3005:
                        continue
                else:
                    if question.id == 30015:
                        continue

                result_id = int(f"{current_user.id}00{question.id}")
                current_app.logger.info(f"Result id: {result_id}")
                q = Results.query.get(result_id)
                if q:
                    db.session.delete(q)
                answer = getattr(form, f"question_{question.id}").data
                if question.question_type in ["mc", "rl"]:
                    answerObj = Answer.query.get(
                        getattr(form, f"question_{question.id}").data)
                    answer_text = answerObj.text
                    if answerObj.next_question != 0:
                        if answerObj.next_question not in [3, 17]:
                            if current_user.doctor:
                                current_app.logger.info(
                                    'doctor for a mc question')
                                next_section = answerObj.next_question
                        else:
                            next_section = answerObj.next_question
                else:
                    answer_text = answer
                    if current_user.doctor:
                        next_section = question.get_next_question()
                        if not next_section:
                            next_section = section.id + 1
                r = Results(id=result_id, answers=answer, answer_text=answer_text, question_id=question.id,
                            user_id=current_user.id)
                db.session.add(r)
                db.session.commit()

                if question.id == 30015:
                    next_section = 4

                if question.id == 50001:
                    next_section = 24

        return redirect(url_for('forms.questionaire',
                                section_id=next_section))

    return render_template('forms/questionaire.html',
                           section=section, form=form)
