from flask import Flask, request, abort, jsonify
from flask_cors import CORS

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    @app.route("/categories")
    def get_categories():
        try:
            categories = Category.query.all()

            categories_for_front_end = {}
            for category in categories:
                categories_for_front_end[category.id] = category.type

            # return successful response
            return jsonify({
                'success': True,
                'categories': categories_for_front_end
            }), 200
        except Exception:
            abort(500)

    @app.route("/questions", methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10

        questions = Question.query.all()

        if len(questions) == 0:
            abort(404)

        formatted_questions = [question.format() for question in questions]

        categories = Category.query.all()
        formatted_categories = [cat.format() for cat in categories]

        curr_cat = [question['category'] for question in formatted_questions]
        current_category = list(set(curr_cat))

        return jsonify({
            'questions': formatted_questions[start:end],
            'total_questions': len(formatted_questions),
            'categories': formatted_categories,
            'current_category': current_category
        }), 200

    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_question_by_id(question_id):
        question = Question.query.filter_by(id=question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()

        return jsonify({'success': True}), 200

    @app.route("/add-questions", methods=['POST'])
    def add_questions():
        data = request.get_json()
        question = data.get('question', '')
        answer = data.get('answer', '')
        difficulty = data.get('difficulty', '')
        category = data.get('category', '')

        try:
            # Create a new question instance
            question = Question(
                question=question,
                answer=answer,
                difficulty=difficulty,
                category=category)

            # save question
            question.insert()

            # return success message
            return jsonify({
                'success': True,
                'message': 'Question successfully created!'
            }), 201

        except Exception:
            # return 422 status code if error
            abort(422)

    @app.route('/search-questions', methods=["POST"])
    def search_questions():
        search_term = request.json.get('searchTerm')

        questions = Question.query.filter(Question.question.ilike
                                          ('%'+search_term+'%')).all()

        len_questions = len(questions)

        if len_questions == 0:
            abort(404)

        formatted_questions = [question.format() for question in questions]

        curr_cat = [question['category'] for question in formatted_questions]
        current_category = list(set(curr_cat))

        return jsonify({
           'questions': formatted_questions,
           'total_questions': len_questions,
           'current_category': current_category
         }), 200

    @app.route("/categories/<int:cat_id>/questions")
    def get_by_category(cat_id):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10

        questions = Question.query.filter_by(category=cat_id).all()
        formatted_question = [question.format() for question in questions]

        response = jsonify({
            'questions': formatted_question[start:end],
            'total_questions': len(formatted_question),
            'current_category': cat_id
           })

        return response

    @app.route("/quizzes", methods=['POST'])
    def quizzes():
        previous_questions = request.json.get('previous_questions')
        quiz_category = request.json.get('quiz_category')

        print(quiz_category)

        if quiz_category['id'] == 0:
            questions_by_category = Question.query.filter
            (Question.id.notin_(previous_questions)).all()

        else:
            questions_by_category = Question.query.filter_by(
              category=quiz_category['id']).filter(Question.id.notin_(
                previous_questions)).all()

        if questions_by_category:
            formatted_questions = [question.format()
                                   for question in questions_by_category]
            return jsonify({'question': formatted_questions[0]}), 200
        else:
            return jsonify({'question': False}), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
             'success': False,
             'error': 404,
             'message': error
          }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': error
          }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': error
          }), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
           'success': False,
           'error': 500,
           'message': error
          }), 500

    return app
