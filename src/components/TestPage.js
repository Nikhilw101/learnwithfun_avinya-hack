import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './TestPage.css';

const TestPage = () => {
  const [answers, setAnswers] = useState({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Questions (Yes/No and C++ related)
  const yesNoQuestions = [
    { id: 1, question: 'Do you have prior experience with programming?', type: 'yesno' },
    { id: 2, question: 'Have you worked with C++ before?', type: 'yesno' },
    { id: 3, question: 'Do you understand the concept of variables?', type: 'yesno' },
  ];

  const cppQuestions = [
    { id: 4, question: 'What is the size of int in C++?', type: 'mcq', options: ['2', '4', '8', '16'] },
    { id: 5, question: 'What does "if" do in C++?', type: 'mcq', options: ['Loop', 'Conditional statement', 'Function', 'Variable'] },
    { id: 6, question: 'Which function is used to get user input in C++?', type: 'mcq', options: ['cout', 'cin', 'scanf', 'printf'] },
  ];

  // Update the answer for a given question ID
  const handleAnswerChange = (questionId, answer) => {
    setAnswers((prevAnswers) => ({
      ...prevAnswers,
      [questionId]: answer,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const user_id = localStorage.getItem('user_id'); // Get user_id from localStorage
      if (!user_id) {
        throw new Error('User not logged in');
      }

      // Format answers for the backend
      const formattedAnswers = [
        ...yesNoQuestions.map((q) => ({
          question_id: q.id,
          user_answer: answers[q.id] || '', // Default to empty string if no answer
        })),
        ...cppQuestions.map((q) => ({
          question_id: q.id,
          user_answer: answers[q.id] || '', // Default to empty string if no answer
        })),
      ];

      // Send answers to the backend
      const response = await axios.post('http://localhost:5000/test/testuserlevel', {
        user_id,
        answers: formattedAnswers,
      });

      const finalLevel = response.data.final_proficiency_level;
      // Navigate based on the final proficiency level
      if (finalLevel.toLowerCase() === 'basic') {
        navigate('/basic'); // Basic level page route
      } else if (finalLevel.toLowerCase() === 'moderate') {
        navigate('/ModerateLevel'); // Moderate level page route
      } else if (finalLevel.toLowerCase() === 'advanced') {
        navigate('/advanced'); // Advanced level page route
      } else {
        // Fallback: navigate to a default dashboard if level is unknown
        navigate('/dashboard', {
          state: { proficiencyLevel: finalLevel },
        });
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to submit test');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="test-container">
      <h2>Test Your C++ Knowledge</h2>
      <form onSubmit={handleSubmit}>
        {/* Yes/No Questions */}
        <div className="question-section">
          <h3>Yes/No Questions</h3>
          {yesNoQuestions.map((q) => (
            <div key={q.id} className="question">
              <p>{q.question}</p>
              <div className="options">
                <label>
                  <input
                    type="radio"
                    name={`question-${q.id}`}
                    value="yes"
                    onChange={() => handleAnswerChange(q.id, 'yes')}
                    checked={answers[q.id] === 'yes'}
                  />
                  Yes
                </label>
                <label>
                  <input
                    type="radio"
                    name={`question-${q.id}`}
                    value="no"
                    onChange={() => handleAnswerChange(q.id, 'no')}
                    checked={answers[q.id] === 'no'}
                  />
                  No
                </label>
              </div>
            </div>
          ))}
        </div>

        {/* C++ Questions */}
        <div className="question-section">
          <h3>C++ Questions</h3>
          {cppQuestions.map((q) => (
            <div key={q.id} className="question">
              <p>{q.question}</p>
              <div className="options">
                {q.options.map((option, index) => (
                  <label key={index}>
                    <input
                      type="radio"
                      name={`question-${q.id}`}
                      value={option}
                      onChange={() => handleAnswerChange(q.id, option)}
                      checked={answers[q.id] === option}
                    />
                    {option}
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? 'Submitting...' : 'Submit Test'}
        </button>
      </form>
    </div>
  );
};

export default TestPage;
