import unittest

from src import rag


class RagAnswerTests(unittest.TestCase):
    def test_retake_answer_keeps_qualifications_without_unrelated_policy(self):
        result = rag.answer(
            "How many times can I retake a failed course, and where do I pay the retake fee?"
        )
        answer = result["answer"].lower()

        self.assertEqual(result["decision"], "grounded")
        self.assertIn("DOC-01", result["sources"])
        self.assertIn("below 50%", answer)
        self.assertIn("school board", answer)
        self.assertIn("only one retake attempt", answer)
        self.assertIn("bursar", answer)
        self.assertNotIn("supplementary", answer)
        self.assertNotIn("school registrar", answer)

    def test_missing_marks_answer_includes_the_required_steps(self):
        result = rag.answer(
            "My results are still missing 30 days after publication — what's the procedure?"
        )
        answer = result["answer"].lower()

        self.assertEqual(result["decision"], "grounded")
        self.assertIn("DOC-02", result["sources"])
        for detail in (
            "course lecturer first",
            "within 7 days",
            "course code, semester, lecturer name",
            "within 14 working days",
            "unofficial fee",
        ):
            self.assertIn(detail, answer)

    def test_pending_status_answer_includes_case_id_and_review_meaning(self):
        result = rag.answer(
            "What format is my support case ID, and what does 'Pending' status mean?"
        )
        answer = result["answer"].lower()

        self.assertIn("DOC-06", result["sources"])
        self.assertIn("DOC-02", result["sources"])
        self.assertIn("case-xxxx", answer)
        self.assertIn("reviewed by staff", answer)

    def test_combined_course_lookup_keeps_both_requested_answers(self):
        result = rag.answer(
            "When are BIT2207 labs, and what do I do if my coursework mark is missing?"
        )
        answer = result["answer"].lower()

        self.assertIn("DOC-08", result["sources"])
        self.assertIn("DOC-02", result["sources"])
        self.assertIn("wednesday 14:00-16:00 cit lab 2", answer)
        self.assertIn("course lecturer first", answer)
        self.assertIn("within 14 working days", answer)
        self.assertNotIn("html", answer)

    def test_mixed_admission_question_keeps_the_answerable_gpa_part(self):
        result = rag.answer(
            "Explain my GPA and tell me if I qualify for admission to Year IV."
        )

        self.assertEqual(result["decision"], "partial")
        self.assertIn("DOC-05", result["sources"])
        self.assertIn("DOC-11", result["sources"])
        self.assertIn("total grade points divided by total credit units", result["answer"])

    def test_fee_waiver_information_is_answered_without_claiming_authority(self):
        result = rag.answer(
            "Can I retake a passed course to improve my grade, and who approves fee waivers?"
        )

        self.assertEqual(result["decision"], "grounded")
        self.assertIn("DOC-01", result["sources"])
        self.assertIn("DOC-10", result["sources"])
        self.assertIn("Head of Department", result["answer"])
        self.assertIn("Bursar and Finance Office", result["answer"])

    def test_unrelated_wifi_question_abstains(self):
        result = rag.answer("What's the WiFi password for the CIT library?")

        self.assertEqual(result["decision"], "abstain")
        self.assertEqual(result["sources"], [])


if __name__ == "__main__":
    unittest.main()
