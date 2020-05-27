import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:123456@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        
        response = self.client().get('/categories')
        self.assertEqual(response.status_code, 200)

        cats = response.json
        self.assertTrue(cats['categories'])
        self.assertTrue(cats['categories'][0])
        self.assertTrue(cats['categories'][0]['id'])
        self.assertTrue(cats['categories'][0]['type'])

        with self.assertRaises(KeyError):
            var = cats['categories'][0]['name']

        with self.assertRaises(IndexError):
            var = cats['categories'][900]

    def test_get_questions(self):
        
        response = self.client().get('/questions')
        self.assertEqual(response.status_code, 200)

        q = response.json
        self.assertIsNotNone(q)
        self.assertGreater(q.__len__(), 0)

        self.assertIn('questions', q)
        self.assertIn('total_questions', q)
        self.assertIn('categories', q)
        self.assertIn('current_category', q)

        with self.assertRaises(KeyError):
            var = q['aaaa']

        with self.assertRaises(KeyError):
            var = q[900]

    def test_add_question(self):
        question = {
            'question': 'questionNumber1',
            'answer': 'answerNumber1',
            'difficulty': '1',
            'category': 2
        }

        response = self.client().post('/add-questions', json=question)
        self.assertTrue(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
    def test_422_add_question(self):
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1
        }
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")    

    def test_delete_question_by_id(self):
        
        questions = self.client().get('/questions')

        data = json.loads(questions.data)

        original_length = len(questions.json)
        self.assertGreater(original_length, 0)

        id_to_delete = data['questions'][original_length]['id']
        questions_deleted = self.client().delete('/questions/' + str(id_to_delete))

        new_length = len(questions_deleted.json)
        self.assertGreater(original_length, new_length) 
        
    def test_422_sent_deleting_non_existing_question(self):
        response = self.client().delete('/questions/a')
        data = json.loads(response.data)    
   
    def test_search_questions(self):
        search_term = {
            'searchTerm': 'w'
        }
        response = self.client().post('/search-questions', json=search_term)
        self.assertEqual(response.status_code, 200)

        data = json.loads(res.data)
        self.assertGreater(len(data), 0)
        
    def test_404_search_question(self):
        new_search = {
            'searchTerm': '',
        }
        res = self.client().post('/questions/search', json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")    
    
    
    def test_get_questions_per_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_get_questions_per_category(self):
        response = self.client().get('/categories/a/questions')
        data = json.loads(response.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
        
        
    def test_play_quiz(self):
        new_quiz = {'previous_questions': [],
                          'quiz_category': {'type': 'Entertainment', 'id': 5}}

        response = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_play_quiz(self):
        new_quiz= {'previous_questions': []}
        response = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()