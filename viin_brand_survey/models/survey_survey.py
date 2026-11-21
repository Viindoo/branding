from odoo import api, models


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    @api.model
    def _prepare_assessment_template_values(self):
        """Return the certification sample with a neutral content.

        The settings come from the core sample; its questions are about a product of the vendor and
        are replaced by questions that are true whatever the product.
        """
        _ = self.env._
        values = super()._prepare_assessment_template_values()
        values.update(
            title=_('Product Knowledge Certification'),
            description=''.join([
                _(
                    'Welcome to this product knowledge certification. '
                    'You will receive 2 random questions out of a pool of 3.'
                ),
                '(<span style="font-style: italic">',
                _('Cheating on your neighbors will not help!'),
                '</span> \N{SMILING FACE WITH SMILING EYES}).<br>',
                _('Good luck!'),
            ]),
            question_and_page_ids=[
                (0, 0, {
                    'title': _('Product Knowledge Certification'),
                    'is_page': True,
                    'question_type': False,
                    'random_questions_count': 2,
                }),
                self._prepare_certification_question(
                    _('What is the main purpose of a product datasheet?'),
                    _('It describes the features and the specifications of the product'),
                    [
                        _('It lists the employees who built the product'),
                        _('It replaces the invoice of the product'),
                    ],
                ),
                self._prepare_certification_question(
                    _('Which of these helps a customer choose the right product?'),
                    _('Comparing the features of the product with the needs of the customer'),
                    [
                        _('Choosing the cheapest product whatever it does'),
                        _('Choosing the product with the longest name'),
                    ],
                ),
                self._prepare_certification_question(
                    _('What should you do when a customer asks a question you cannot answer?'),
                    _('Find the answer and come back to the customer'),
                    [
                        _('Make up an answer'),
                        _('Ignore the question'),
                    ],
                ),
            ],
        )
        return values

    @api.model
    def _prepare_certification_question(self, title, correct_answer, wrong_answers):
        return (0, 0, {
            'title': title,
            'question_type': 'simple_choice',
            'suggested_answer_ids': [(0, 0, {'value': correct_answer, 'is_correct': True, 'answer_score': 10})]
            + [(0, 0, {'value': wrong_answer}) for wrong_answer in wrong_answers],
        })
