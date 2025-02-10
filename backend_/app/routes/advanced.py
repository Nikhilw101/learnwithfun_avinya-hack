import requests
from flask import Blueprint, jsonify
from app.models.advanced_level import AdvancedLevel
from app.db import db
import logging

# Create a Blueprint for advanced_learning
advanced_learning = Blueprint('advanced_learning', __name__)

# Generative API endpoint and key
GENERATIVE_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
GENERATIVE_API_KEY = "AIzaSyDgxQNnsxs35NorPl78EM-jlRy-QRmDJeo"

# Advanced-level concepts
sub_levels = {
    1: ["C++ Metaprogramming", "C++ Concurrency"],
    2: ["C++ Memory Management", "C++ Performance Optimization"],
    3: ["C++ Design Patterns", "C++ Advanced Templates"],
    4: ["C++ Networking", "C++ Graphics Programming"]
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_content_with_generative_api(prompt):
    try:
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(
            f"{GENERATIVE_API_URL}?key={GENERATIVE_API_KEY}",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            logger.error(f"Failed to generate content: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return None

def get_learning_content():
    content = []
    for level, concepts in sub_levels.items():
        for concept in concepts:
            prompt = f"Explain the concept of {concept} in C++ programming in 100 words."
            description = generate_content_with_generative_api(prompt)
            content.append({
                "sub_level": level,
                "concept": concept,
                "description": description or "Description not available."
            })
    return content

@advanced_learning.route('/get_advanced_content', methods=['GET'])
def add_learning_content():
    try:
        content = get_learning_content()
        added_content = []
        for item in content:
            new_content = AdvancedLevel(
                sub_level=item['sub_level'],
                concept=item['concept'],
                description=item['description']
            )
            db.session.add(new_content)
            added_content.append({"concept": item['concept'], "description": item['description']})
        db.session.commit()
        return jsonify({"message": "Advanced content added!", "added_content": added_content}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": "Failed to add content"}), 500

@advanced_learning.route('/get_quiz/<concept>', methods=['GET'])
def get_quiz(concept):
    try:
        prompt = f"Generate 3 quiz questions with answers for {concept} in C++. Provide correct answers."
        quiz_content = generate_content_with_generative_api(prompt)
        if not quiz_content:
            return jsonify({"error": "Quiz generation failed"}), 500

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

        return jsonify({"quiz_data": {"concept": concept, "questions": questions}}), 200
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500