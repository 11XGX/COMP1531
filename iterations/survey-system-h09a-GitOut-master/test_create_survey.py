import unittest
import server #create databases
from sqlalchemy import exc
import os
from question import TextQuestion
from functions import *

class TestCreateSurvey(unittest.TestCase):
    def setUp(self):
        server.createDatabases()
        self.questions = [TextQuestion('TXTMANDTEST', True, "Hello how are you?")]

    def test_createSurveyNormal(self):
        self.assertEqual('TESTKEY2', createSurv('TESTKEY2', True, 1, 'Test Survey', 'Desc'))
        survey = loadSurv('TESTKEY2 ')

        addQuestion('TESTKEY2', self.questions[0].id, True)

    def test_createSurveyNoQuestion(self):
        surveyKey =  createSurv('TESTKEY3', True, 1, 'Test Survey', 'Desc')
        survey = loadSurv(surveyKey)

        with self.assertRaises(ValueError):
            nextPhaseSurvey(survey)

    def test_surveyAddNullQuestion(self):
        surveyKey =  createSurv('TESTKEY4', True, 1, 'Test Survey', 'Desc')
        survey = loadSurv(surveyKey)

        with self.assertRaises(ValueError):
            addQuestion('TESTKEY4', None, True)

    def test_deleteSurvey(self):
        surveyKey =  createSurv('TESTKEY5', True, 1, 'Test Survey', 'Desc')
        survey = loadSurv(surveyKey)

        self.assertEqual(survey.key, 'TESTKEY5')

        deleteSurvey(None, 'TESTKEY5')
        self.assertEqual(None, loadSurv(surveyKey))

    def tearDown(self):
        os.remove('data.db')

if __name__ == "__main__":
    unittest.main()
