import json
import unittest
from edu_trainer_ai.core import EduService,Learner,Lesson

class FakeModel:
    def __init__(self,response):
        self.response=response
        self.calls=0
    def complete(self,prompt):
        self.calls+=1
        return self.response

class EduTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.svc=EduService()
        cls.student=Learner("python-foundations")
        cls.ml=Learner("ml-fundamentals")

    def test_scope_by_course(self):
        search=self.svc.search(self.student,"ML Precision Recall train validation")
        self.assertTrue(all("ML-" not in x["id"] for x in search["evidence"]))

    def test_trainer_only_hidden(self):
        data=self.svc.search(self.student,"Đáp án chỉ dành cho trainer")
        self.assertNotIn("PY-SECRET",[x["id"] for x in data["evidence"]])
        other=self.svc.search(Learner("python-foundations","trainer"),"đề thi đáp án trainer")
        self.assertIn("PY-SECRET",[x["id"] for x in other["evidence"]])

    def test_retrieval_source(self):
        info=self.svc.search(self.student,"Python __init__ class")
        self.assertEqual(info["evidence"][0]["id"],"PY-004")
        self.assertIn("synthetic://",info["evidence"][0]["source"])

    def test_quiz_answer_key_not_exposed(self):
        quiz=self.svc.quiz(self.student,"01-intro")
        self.assertEqual(quiz["status"],"quiz_ready")
        self.assertNotIn("correct",str(quiz))
        self.assertEqual(quiz["questions"][0]["id"],"PY-Q1")

    def test_quiz_practice_grade(self):
        result=self.svc.grade_quiz(self.student,{"PY-Q1":"A","PY-Q2":"A"})
        self.assertEqual(result["correct"],1)
        self.assertFalse(result["recorded_to_lms"])
        self.assertTrue(result["needs_trainer_review"])

    def test_invalid_quiz(self):
        self.assertEqual(self.svc.grade_quiz(self.student,{"ML-Q1":"B"})["status"],"invalid_submission")

    def test_rubric_has_no_official_grade(self):
        good=self.svc.rubric_feedback(self.student,"PY-R1","def foo(): return 1. unittest assert")
        self.assertEqual(good["observed_criteria"],2)
        self.assertFalse(good["grade_official"])
        self.assertTrue(good["trainer_review_required"])
        miss=self.svc.rubric_feedback(self.student,"ML-R1","train validation")
        self.assertEqual(miss["status"],"rubric_not_found")

    def test_learning_path_static(self):
        path=self.svc.learning_path(self.student,["01-intro"])
        self.assertEqual(path["recommended_next_module"],"02-control")
        self.assertTrue(path["synthetic"])

    def test_grounded_feedback_citation_membership(self):
        hit=self.svc.search(self.student,"Python __init__ class")["evidence"][0]["id"]
        model=FakeModel(json.dumps({"feedback":"Review the class constructor.","citation_ids":[hit],"needs_review":True}))
        r=self.svc.draft_grounded_feedback(self.student,"Python __init__ class",model)
        self.assertEqual(r["status"],"unverified_draft")
        self.assertEqual(model.calls,1)
        self.assertTrue(r["trainer_review_required"])

    def test_madeup_citation_rejected(self):
        model=FakeModel(json.dumps({"feedback":"Wrong evidence","citation_ids":["ML-001"],"needs_review":True}))
        r=self.svc.draft_grounded_feedback(self.student,"Python __init__ class",model)
        self.assertEqual(r["status"],"rejected_citations")

    def test_unparseable_model_response_fails_closed(self):
        model=FakeModel("not JSON")
        result=self.svc.draft_grounded_feedback(self.student,"Python __init__ class",model)
        self.assertEqual(result["status"],"invalid_model_response")

    def test_no_evidence_skips_model(self):
        model=FakeModel("{}")
        res=self.svc.draft_grounded_feedback(self.student,"tàu vũ trụ thiên hà",model)
        self.assertEqual(res["status"],"abstained")
        self.assertEqual(model.calls,0)

    def test_agent_denies_unsupported_tool(self):
        self.assertEqual(self.svc.run_tool("publish_grade",self.student,{})["status"],"denied_tool")

    def test_unsupported_questions_do_not_create_evidence(self):
        for question in ["Thời tiết Sao Hỏa tối nay ra sao?",
                         "Cho tôi đáp án tài liệu dành riêng trainer"]:
            with self.subTest(question=question):
                result=self.svc.search(self.student,question)
                self.assertEqual(result["status"],"abstained")
                self.assertFalse(result["evidence"])

    def test_eval_has_no_access_leakage(self):
        from edu_trainer_ai.evaluate import evaluate
        report=evaluate()
        self.assertEqual(report["access_leakage_count"],0)
        self.assertGreater(report["answerable"],4)

    def test_invalid_lesson_schema(self):
        with self.assertRaises(ValueError):
            Lesson.parse({"roles":["student"]})

if __name__=="__main__":unittest.main()
