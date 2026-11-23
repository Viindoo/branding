from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestCertificationTemplate(TransactionCase):

    def _sample(self):
        values = self.env['survey.survey']._prepare_assessment_template_values()
        return self.env['survey.survey'].create(values)

    def test_the_certification_sample_names_no_product(self):
        survey = self._sample()
        self.assertTrue(survey.title)
        texts = [survey.title, survey.description, *survey.question_and_page_ids.mapped('title')]
        texts += survey.question_and_page_ids.suggested_answer_ids.mapped('value')
        for text in texts:
            self.assertNotIn('Odoo', text)
            self.assertNotIn('ODOO', text)
            self.assertNotIn('Viindoo', text)

    def test_every_question_of_the_certification_sample_has_exactly_one_true_answer(self):
        questions = self._sample().question_and_page_ids.filtered(lambda question: not question.is_page)
        self.assertEqual(len(questions), 3)
        for question in questions:
            with self.subTest(question=question.title):
                correct = question.suggested_answer_ids.filtered('is_correct')
                self.assertEqual(len(correct), 1)
                self.assertGreater(correct.answer_score, 0)
                self.assertEqual(len(question.suggested_answer_ids), 3)
