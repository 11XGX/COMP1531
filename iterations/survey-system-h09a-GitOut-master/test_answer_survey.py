import unittest
import server #create databases
from sqlalchemy import exc
import os
from question import TextQuestion
from functions import *

class TestEnrolSurvey(unittest.TestCase):
    def setUp(self):
        server.createDatabases()
        TextQuestion('question', True, "Hello how are you?")
        self.survey = createSurv('Survey', True, 1, 'Test Survey', 'Desc')
        self.assertEqual(1, addQuestion('Survey', 'question', True))
      
    def test_answer_normal(self):
        self.assertEqual(1, saveResponse(loadSurv('Survey'), '50', ['I am good']))

    def test_answer_not_answer_optional_q(self):
        with self.assertRaises(ValueError):
            saveResponse(loadSurv('Survey'), '51', [''])

    def test_answer_invalid_student(self):
        self.assertEqual(-1, saveResponse(loadSurv('Survey'), '-1', ['Hello']))

    def test_answer_invalid_answers(self):
        with self.assertRaises(ValueError):
            saveResponse(loadSurv('Survey'), '52', [])


    def tearDown(self):
        os.remove('data.db')

if __name__ == "__main__":
    unittest.main()
