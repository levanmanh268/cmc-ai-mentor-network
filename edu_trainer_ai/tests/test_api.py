import unittest
try:
    from fastapi.testclient import TestClient
    from edu_trainer_ai.api import app
    client=TestClient(app)
except ImportError:
    client=None

@unittest.skipIf(client is None, "FastAPI/httpx optional in root CI")
class EduApiTests(unittest.TestCase):
    def test_health_student_scope(self):
        r=client.get("/health")
        self.assertEqual(r.status_code,200)
        self.assertFalse(r.json()["official_lms_grades"])
    def test_trainer_only_not_exposed(self):
        r=client.post("/course/search",json={"question":"đề thi trainer đáp án"})
        self.assertEqual(r.status_code,200)
        self.assertNotIn("PY-SECRET",[x["id"] for x in r.json()["evidence"]])
    def test_quiz_answer_key_hidden(self):
        r=client.post("/quiz",json={"module":"01-intro"})
        self.assertEqual(r.status_code,200)
        self.assertNotIn("correct",str(r.json()))
    def test_quiz_score_provisional(self):
        r=client.post("/quiz/grade",json={"answers":{"PY-Q1":"A"}})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()["correct"],1)
        self.assertFalse(r.json()["recorded_to_lms"])
    def test_rubric_not_official_grade(self):
        r=client.post("/rubric/feedback",json={"rubric_id":"PY-R1","submission":"def f(): return 1; unittest test assert"})
        self.assertEqual(r.status_code,200)
        self.assertTrue(r.json()["trainer_review_required"])
    def test_invalid_request(self):
        self.assertEqual(client.post("/course/search",json={"question":""}).status_code,422)
        self.assertEqual(client.post("/rubric/feedback",json={"rubric_id":"PY-R1","submission":""}).status_code,422)
