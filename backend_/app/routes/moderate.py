import requests
from flask import Blueprint, jsonify
from app.models.moderate_level import ModerateLevel
from app.db import db
import logging


# Create a Blueprint for moderate_learning
moderate_learning = Blueprint('moderate_learning', __name__)

# Generative API endpoint and key
GENERATIVE_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
GENERATIVE_API_KEY = "AIzaSyDgxQNnsxs35NorPl78EM-jlRy-QRmDJeo"

# Set up the array with sub-levels and concepts for Moderate Level
sub_levels = {
    1: ["C++ Templates", "C++ Exception Handling"],
    2: ["C++ Smart Pointers", "C++ Multithreading"],
    3: ["C++ Lambda Expressions", "C++ Move Semantics"],
    4: ["C++ Standard Library", "C++ File Handling"]
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to generate content using the Generative API with fallback
def generate_content_with_generative_api(prompt):
    try:
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        response = requests.post(
            f"{GENERATIVE_API_URL}?key={GENERATIVE_API_KEY}",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            logger.error(f"Failed to generate content: {response.status_code}, {response.text}")
            # Fallback content if API resource is exhausted or other error occurs
            return f"Default explanation for: {prompt}"
    except Exception as e:
        logger.error(f"Error generating content with Generative API: {str(e)}")
        return f"Default explanation for: {prompt}"

# Function to get learning content formatted as a list of dictionaries
def get_learning_content():
    content = []    
    for level, concepts in sub_levels.items():
        for concept in concepts:
            # Updated prompt for a more detailed description (200 words, including key features, usage, advantages, and common pitfalls)
            prompt = f"Provide a detailed explanation (approximately 200 words) of the concept of {concept} in C++ programming. Include key features, common usage scenarios, advantages, and any potential pitfalls."
            description = generate_content_with_generative_api(prompt)
            if description:
                content.append({
                    "sub_level": level,
                    "concept": concept,
                    "description": description
                })
            else:
                content.append({
                    "sub_level": level,
                    "concept": concept,
                    "description": "Description not available."
                })
    return content

# Route to fetch and store learning content in the database
@moderate_learning.route('/get_moderate_content', methods=['GET'])
def add_learning_content():
    try:
        content = get_learning_content()  # Fetch learning content (with fallbacks if needed)
        added_content = []
        for item in content:
            new_content = ModerateLevel(
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
            "message": "Moderate learning content added successfully!",
            "added_content": added_content
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding moderate learning content: {str(e)}")
        return jsonify({"error": "Failed to add moderate learning content"}), 500

# Route to fetch quiz questions for a given concept
@moderate_learning.route('/get_quiz/<concept>', methods=['GET'])
def get_quiz(concept):
    try:
        prompt = f"Generate 3 quiz questions with answers for the concept of {concept} in C++ programming. Provide the correct answer for each question."
        quiz_content = generate_content_with_generative_api(prompt)
        if not quiz_content:
            logger.error(f"Failed to generate quiz questions for '{concept}'")
            return jsonify({"error": "Failed to generate quiz questions"}), 500
        # Parse the quiz content into structured questions and answers
        questions = []
        quiz_lines = quiz_content.split("\n")
        current_question = None
        for line in quiz_lines:
            if line.startswith("**Question"):
                if current_question:
                    questions.append(current_question)
                current_question = {"question": "", "answer": "", "code": ""}
            elif line.startswith("**Answer:"):
                current_question["answer"] = line.replace("**Answer:**", "").strip()
            elif line.startswith("```"):
                current_question["code"] = line.strip("```").strip()
            elif current_question:
                if not current_question["question"]:
                    current_question["question"] = line.strip()
                else:
                    current_question["answer"] += "\n" + line.strip()
        if current_question:
            questions.append(current_question)
        quiz_data = {
            "concept": concept,
            "questions": questions
        }
        return jsonify({"quiz_data": quiz_data}), 200
    except Exception as e:
        logger.error(f"Error fetching quiz for '{concept}': {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
