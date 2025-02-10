from flask import Blueprint, request, jsonify
from app.models.user import User
from app.db import db  # Ensure db is imported here

test_routes = Blueprint('test_routes', __name__)

# Yes/No Questions
yes_no_questions = [
    {"question": "Do you have prior experience with programming?", "answer": "yes"},  # Correct answer is "yes"
    {"question": "Have you worked with C++ before?", "answer": "no"},  # Correct answer is "no"
    {"question": "Do you understand the concept of variables?", "answer": "yes"}  # Correct answer is "yes"
]

# Assessment Questions (C++ related)
assessment_questions = [
    {"question": "What is the size of int in C++?", "answer": "4"},  # Correct answer is 4 bytes
    {"question": "What does 'if' do in C++?", "answer": "Conditional statement"},  # Correct answer is Conditional statement
    {"question": "Which function is used to get user input in C++?", "answer": "cin"}  # Correct answer is cin
]

@test_routes.route('/testuserlevel', methods=['POST'])
def test_user_level():
    data = request.get_json()
    
    # Extract answers submitted by the user
    user_answers = data.get('answers', [])
    
    # Check if the number of answers is correct (Yes/No questions + assessment questions)
    if len(user_answers) != len(yes_no_questions) + len(assessment_questions):
        return jsonify({"error": "Incorrect number of answers"}), 400
    
    # Evaluate the Yes/No answers first
    yes_no_correct_answers = 0
    for i in range(len(yes_no_questions)):
        question = user_answers[i]
        user_answer = question.get("user_answer", "").lower()
        correct_answer = yes_no_questions[i].get("answer", "").lower()
        
        # Check if the user's answer matches the correct answer (Yes/No questions)
        if user_answer == correct_answer:
            yes_no_correct_answers += 1

    # Determine proficiency level from Yes/No questions
    yes_no_level = determine_yes_no_level(yes_no_correct_answers)
    
    # Evaluate the assessment questions
    assessment_correct_answers = 0
    for i in range(len(assessment_questions)):
        question = user_answers[i + len(yes_no_questions)]  # Skip the Yes/No questions
        user_answer = question.get("user_answer", "").lower()
        correct_answer = assessment_questions[i].get("answer", "").lower()
        
        # Check if the user's answer matches the correct answer (Assessment questions)
        if user_answer == correct_answer:
            assessment_correct_answers += 1

    # Determine final proficiency level based on assessment questions
    assessment_level = determine_level(assessment_correct_answers)

    # Combine Yes/No and assessment levels to determine final proficiency level
    final_level = combine_levels(yes_no_level, assessment_level)
    
    # Save user proficiency level in the database
    user_id = data.get('user_id')  # Assuming you send user_id in the request
    user = User.query.filter_by(id=user_id).first()
    if user:
        user.proficiency_level = final_level
        db.session.commit()
    
    return jsonify({
        "message": "Test evaluated successfully",
        "correct_answers_yes_no": yes_no_correct_answers,
        "correct_answers_assessment": assessment_correct_answers,
        "final_proficiency_level": final_level
    })

def determine_yes_no_level(correct_answers):
    # Determine proficiency level based on Yes/No questions
    if correct_answers == 0:
        return "Basic"
    elif 1 <= correct_answers <= 2:
        return "Moderate"
    else:
        return "Advanced"

def determine_level(correct_answers):
    # Determine proficiency level based on assessment questions
    if correct_answers == 0:
        return "Basic"
    elif 1 <= correct_answers <= 2:
        return "Moderate"
    else:
        return "Advanced"

def combine_levels(yes_no_level, assessment_level):
    # Combine the results of Yes/No and assessment questions to determine final level
    if yes_no_level == "Advanced" and assessment_level == "Advanced":
        return "Advanced"
    elif yes_no_level == "Moderate" or assessment_level == "Moderate":
        return "Moderate"
    else:
        return "Basic"
