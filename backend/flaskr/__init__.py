
# ===================== import fields here  ==================================


import os
from flask import (
  Flask,
  request,
  abort,
  jsonify,
  json,
  flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import (
  setup_db,
  Question,
  Category
)

# ===================== import fields here  ==================================





# --------------------------- paginate questions (function here) ----------------------
QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)  # here we set the page with max of 
    start = (page - 1) * QUESTIONS_PER_PAGE       # 10 question per page 
    end = start + QUESTIONS_PER_PAGE              # we will use this function down later 

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

# --------------------------- paginate questions (function here) ----------------------



# start writing the code in create app function
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)


  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs   
  '''
  # I finish this down under the TODO -2-

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow 
  '''
  @app.after_request
  def afterRequest(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PATCH, DELETE')
    return response
  
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET']) # set the app route to the categories
  def get_categrories():
    categories = Category.query.all() # get all the categories 
    categories_dict = {}
    for category in categories: # for loop to get category in categories 
      categories_dict[category.id] = category.type
    # return category data to view
    return jsonify({ # return the jsonify
        'success': True,
        'categories': categories_dict
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_question():

    selection = Question.query.all() # get all the questions and save it in (selection variable)
    total_questions = len(selection) # set the total question by len the selection or len all the question 
    current_questions = paginate_questions(request, selection) 

        # get all categories and add to dict
    categories = Category.query.all()
    categories_dict = {}
    for category in categories:
      categories_dict[category.id] = category.type

        # return data to view
    return jsonify({ 
        'success': True,
        'questions': current_questions,
        'total_questions': total_questions,
        'categories': categories_dict
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE']) # now here we want to delete the question
  def delete(question_id):
    try:
            # get question by id, use one_or_none to only turn one result
            # or call exception if none selected
      question = Question.query.filter_by(id=question_id).one_or_none()

            # abort if question not found
      if question is None:
        abort(404)

            # delete and return success message
      else:
        question.delete()

      return jsonify({
          'success': True,
          'deleted': question_id
      })
    except:
            # abort if there's a problem deleting the question
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods = ['POST']) # now we will set the question difficulty 
  def create_questions():
    body = request.get_json() 
    x = body # I set x variable to the body to make it shorter to write < i didnt choose x from the beginning because its not suitable >
    if not('question' in x and 'answer' in x and 'difficulty' in x and 'category' in x): # here I set if statement to make sure every thing is going good and if there is any wrong thing or missing thing I want to give an error or abort back to the client 
      return abort(422)
    theQuestion = Question(
      question = body['question'],
      answer = body['answer'],
      difficulty= body['difficulty'],
      category = body['category']
    )
    theQuestion.insert()
    return jsonify({ # return jsonify 
      "success":True,
      "created":theQuestion.format()
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST']) # now we will set a search statement 
  def search_questions():

        # Get search term from request data
    data = request.get_json()
    search_term = data.get('searchTerm', None)

        # Return 422 status code if empty search term is sent
    if search_term == '':
      abort(422)

    try:
            # get all questions that has the search term substring
      if search_term:
        questions = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')).all()

            # if there are no questions for search term return 404
      if len(questions) == 0:
        abort(404)

            # paginate questions
      paginated_questions = get_paginated_questions(
                request, questions,
                QUESTIONS_PER_PAGE)

            # return response if successful
      return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(Question.query.all())
            }), 200

    except Exception:
            # This error code is returned when 404 abort
            # raises exception from try block
      abort(404)

   
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET']) # now we want appear only the question that relate to a category
  def get_the_question_by_category(category_id): 
    try:
      questions = Question.query.filter(Question.category == str(category_id)).all()

      return jsonify({
              'success': True,
              'questions': [question.format() for question in questions],
              'total_questions': len(questions),
              'current_category': category_id
          })
    except:
      abort(404) # if anything went wrong this error must appear its 404
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST']) # here we want to set the play 
  def get_quizzes():
    try:
      body = request.get_json()

      category = body.get('quiz_category')
      previous_questions = body.get('previous_questions')

            # If 'ALL' categories is 'clicked', filter available Qs
      if category['type'] == 'click':
        available_questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
            # Filter available questions by chosen category & unused questions
      else:
        available_questions = Question.query.filter_by(category=category['id']).filter(Question.id.notin_((previous_questions))).all()

            # randomly select next question from available questions
      new_question = available_questions[random.randrange(0, len(available_questions))].format() if len(available_questions) > 0 else None

      return jsonify({
          'success': True,
          'question': new_question
        })
    except:
      abort(422)

  

  @app.errorhandler(400)
  def bad_request_error(error):
      return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 422

  return app

    