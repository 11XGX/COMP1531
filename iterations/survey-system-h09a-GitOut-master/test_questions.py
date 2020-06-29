import unittest
import server #create databases
from sqlalchemy import exc
from question import Question,QuestionHandler,  TextQuestion, MCQ
import os

class TestQuestions(unittest.TestCase):
    def setUp(self):
        server.createDatabases()


    def test_createMandatoryQ(self):
        mandatoryTextQ = TextQuestion('TXTMANDTEST', True, "Hello how are you?")
        
        self.assertEqual(mandatoryTextQ.compulsory, True)

    def test_createOptionalQ(self):
        optionalTextQ = TextQuestion('TXTOPTTEST', False, "Hello how are you?")
        
        self.assertEqual(optionalTextQ.compulsory, False)

    def test_createMultipleChoice(self):
        mcQuestion = MCQ('MCQTEST', False, "Hello how are you?", ['good', 'bad'])
        
        self.assertEqual(mcQuestion.type, 'MCQ')
 
    def test_createNoNameQuestion(self):
        with self.assertRaises(ValueError):
            mcQuestion = MCQ('', False, "Hello how are you?", ['good', 'bad'])

    def test_createNoResponseMCQ(self):
        with self.assertRaises(ValueError):
            mcQuestion = MCQ('', False, "Hello how are you?", [])

    def test_deleteQuestion(self):
        mcQuestion = MCQ('MCQTEST', False, "Hello how are you?", ['good', 'bad'])
        from functions import loadKeyedQuestion
        
        self.assertEqual(False, loadKeyedQuestion('MCQTEST').deleted)


        QuestionHandler.deleteQuestion('MCQTEST')

        self.assertEqual(True, loadKeyedQuestion('MCQTEST').deleted)

    def tearDown(self):
        os.remove('data.db')

if __name__ == "__main__":
    unittest.main()

