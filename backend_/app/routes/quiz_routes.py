import wikipediaapi
from flask import Blueprint, jsonify, request
import requests
from app.models.base_level import BaseLevel
from app.db import db

# Create a Blueprint for cpp_learning
cpp_learning = Blueprint('cpp_learning', __name__)

# Initialize Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia('en')

# Set up the array with sub-levels and concepts for Base Level
sub_levels = {
    1: ["C++ Syntax", "C++ Variables"],
    2: ["C++ Loops", "C++ Conditions"],
    3: ["C++ Functions", "C++ Pointers"],
    4: ["C++ Object-Oriented Programming", "C++ Data Structures"]
}

# Function to fetch data from Wikipedia
def fetch_concept_details(concept):
    try:
        page = wiki_wiki.page(concept)
        if page.exists():
            return page.title, page.summary
        else:
            return concept, "Description not found."
    except Exception as e:
        return concept, f"Error: {str(e)}"

# Function to get learning content formatted as a list of dictionaries
def get_learning_content():
    content = []
    
    for level, concepts in sub_levels.items():
        for concept in concepts:
            title, description = fetch_concept_details(concept)
            content.append({
                "sub_level": level,
                "concept": title,
                "description": description
            })
    
    return content

# Route to fetch and store learning content in the database
@cpp_learning.route('/get_basic_content', methods=['GET'])
def add_learning_content():
    content = get_learning_content()  # Fetch learning content from Wikipedia
    added_content = []

    for item in content:
        new_content = BaseLevel(
            sub_level=item['sub_level'],
            concept=item['concept'],
            description=item['description']
        )
        db.session.add(new_content)
        added_content.append({
            "concept": item['concept'],
            "description": item['description']
        })
    
    db.session.commit()
    
    return jsonify({
        "message": "Learning content added successfully!",
        "added_content": added_content
    }), 200


# Quiz Routes - Fetch quizzes from external API and return quizzes without storing them in the database
quiz_routes = Blueprint('quiz_routes', __name__)

# API Configuration
RAPIDAPI_KEY = "cafb9b628dmshcd34b49d7431c42p1f4d87jsn359b1a9c01c2"
RAPIDAPI_HOST = "c-quiz-questions.p.rapidapi.com"
QUIZ_API_URL = "https://c-quiz-questions.p.rapidapi.com/v1/cpp_questions"

# Fetch quizzes from API
def fetch_quizzes(concept, count=5):
    headers = {
        "X-Rapidapi-Key": RAPIDAPI_KEY,
        "X-Rapidapi-Host": RAPIDAPI_HOST
    }
    params = {
        "count": count,
        "topic": concept.lower().replace(" ", "_")  # Match topic with concept
    }
    response = requests.get(QUIZ_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Route to fetch quizzes for a concept without storing them in the database
@quiz_routes.route('/get_quizzes/<string:concept>', methods=['GET'])
def get_quizzes(concept):
    quizzes = fetch_quizzes(concept)
    if not quizzes:
        return jsonify({"error": "Failed to fetch quizzes"}), 500

    added_quizzes = []
    for quiz in quizzes:
        added_quizzes.append({
            "concept": concept,
            "question": quiz['question'],
            "options": quiz['options'],
            "correct_answer": quiz['correct_answer']
        })
    
    return jsonify({
        "message": "Quizzes fetched successfully!",
        "quizzes": added_quizzes
    }), 200

# Route to check user answers (no quiz storage involved)
@quiz_routes.route('/check_answers', methods=['POST'])
def check_answers():
    data = request.get_json()
    user_answers = data.get('answers', [])  # List of {quiz_id, user_answer}
    results = []

    for answer in user_answers:
        # Here, instead of querying the database, we assume the quiz answers are passed directly
        is_correct = (answer['correct_answer'] == answer['user_answer'])
        results.append({
            "question": answer['question'],
            "correct_answer": answer['correct_answer'],
            "user_answer": answer['user_answer'],
            "is_correct": is_correct
        })
    
    return jsonify({"results": results}), 200
