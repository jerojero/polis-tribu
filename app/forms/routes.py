from flask import render_template, redirect, url_for, current_app
from flask_login import login_required, current_user

from app import db
from . import bp
from .forms_forms import create_questionaire, make_question_form
from .forms_forms import AddQuestionForm, AddAnswerForm, LinkQuestionsForm
from wtforms import RadioField, StringField, BooleanField, SubmitField
from wtforms.validators import Optional
from app.models import Question, Section, Results, Answer, Payment

# utils
from app.utils import create_question, create_section, create_answer


@bp.route('/questionaire/<int:section_id>', methods=['GET', 'POST'])
@bp.route('/questionaire/', methods=['GET', 'POST'])
@login_required
def questionaire(section_id=None):
    if not section_id:
        section_id = 1
    section = Section.query.filter_by(id=section_id).first()
    current_app.logger.info(f"Section: {section}")

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
                account_number = str(form.account_number)
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
                result_id = int(f"{current_user.id}00{question.id}")
                current_app.logger.info(f"Result id: {result_id}")
                q = Results.query.get(result_id)
                if q:
                    db.session.delete(q)
                answer = getattr(form, f"question_{question.id}").data
                if question.question_type == "mc":
                    answerObj = Answer.query.get(
                        getattr(form, f"question_{question.id}").data)
                    answer_text = answerObj.text
                    if answerObj.next_question != 0:
                        next_section = answerObj.next_question
                else:
                    answer_text = answer
                r = Results(id=result_id, answers=answer, answer_text=answer_text, question_id=question.id,
                            user_id=current_user.id)
                db.session.add(r)
                db.session.commit()

        return redirect(url_for('forms.questionaire',
                                section_id=next_section))

    return render_template('forms/questionaire.html',
                           section=section, form=form)


@bp.route('/add_question/', methods=['GET', 'POST'])
@login_required
def add_question():
    question_form = AddQuestionForm()
    answer_form = AddAnswerForm()
    link_form = LinkQuestionsForm()

    if question_form.validate_on_submit():

        title = question_form.title.data
        question_type = question_form.question_type.data
        description = question_form.description.data
        section_id = int(question_form.section.data)
        optional = question_form.optional.data
        tail = question_form.optional.data

        if not Section.query.get(section_id):
            create_section(tail=tail)

        create_question(
            title,
            question_type,
            description=description,
            section_id=section_id,
            optional=optional)

    if answer_form.validate_on_submit():
        current_app.logger.info("answer_form validates")

        text = answer_form.text.data
        associated_question = int(answer_form.associated_question.data)
        next_question = int(answer_form.next_question.data)

        create_answer(
            text, associated_question, next_question=next_question
        )

    if link_form.validate_on_submit():
        current_app.logger.info("link_form validates")

    return render_template('forms/add_question.html', answer_form=answer_form,
                           link_form=link_form, question_form=question_form)
