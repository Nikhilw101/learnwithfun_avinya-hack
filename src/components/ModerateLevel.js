import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './ModerateLevel.css';

const ModerateLevel = () => {
  const [slides, setSlides] = useState([]); // Combined slides (content + quiz)
  const [quizzes, setQuizzes] = useState({}); // Quiz questions for each concept
  const [userAnswers, setUserAnswers] = useState({}); // User's selected answers
  const [solutionVisible, setSolutionVisible] = useState({}); // Toggle correct answer visibility
  const [currentSlide, setCurrentSlide] = useState(0); // Current slide index
  const [loading, setLoading] = useState(true); // Loading state
  const navigate = useNavigate();

  // Fetch moderate-level content and quiz data on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch moderate-level content
        const contentRes = await axios.get('http://localhost:5000/moderate/get_moderate_content');
        const contents = contentRes.data.added_content; // Array of { concept, description }

        // Fetch quiz questions for each concept
        const quizMap = {};
        for (const item of contents) {
          try {
            const quizRes = await axios.get(
              `http://localhost:5000/moderate/get_quiz/${encodeURIComponent(item.concept)}`
            );
            quizMap[item.concept] = quizRes.data.quiz_data.questions; // Array of questions
          } catch (err) {
            console.error(`Error fetching quiz for ${item.concept}:`, err);
            quizMap[item.concept] = []; // Fallback to empty array
          }
        }
        setQuizzes(quizMap);

        // Create combined slides: for each concept, one content slide and one quiz slide
        const combinedSlides = [];
        contents.forEach((item) => {
          combinedSlides.push({ type: 'content', data: item }); // Content slide
          combinedSlides.push({ type: 'quiz', data: item }); // Quiz slide
        });
        setSlides(combinedSlides);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Toggle solution visibility for a given concept and question index
  const toggleSolution = (concept, questionIndex) => {
    setSolutionVisible((prev) => ({
      ...prev,
      [concept]: {
        ...prev[concept],
        [questionIndex]: !prev[concept]?.[questionIndex],
      },
    }));
  };

  // Handle user's answer selection for a quiz question
  const handleAnswerSelect = (concept, questionIndex, answer) => {
    setUserAnswers((prev) => ({
      ...prev,
      [concept]: {
        ...prev[concept],
        [questionIndex]: answer,
      },
    }));
  };

  // Navigate to the next slide or submit answers
  const handleNext = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide((prev) => prev + 1);
    } else {
      handleSubmit();
    }
  };

  // Navigate to the previous slide
  const handlePrevious = () => {
    if (currentSlide > 0) {
      setCurrentSlide((prev) => prev - 1);
    }
  };

  // Submit user answers and navigate to the Advanced Level page
  const handleSubmit = async () => {
    try {
      const userId = localStorage.getItem('user_id');
      await axios.post('http://localhost:5000/moderate/submit_answers', {
        userId,
        answers: userAnswers,
      });
      navigate('/advanced'); // Navigate to the Advanced Level page
    } catch (error) {
      console.error('Error submitting answers:', error);
    }
  };

  if (loading) return <div className="loading text-center">Loading content...</div>;
  if (slides.length === 0) return <div className="loading text-center">No content available.</div>;

  // Current slide data
  const currentSlideData = slides[currentSlide];
  const concept = currentSlideData.data;

  return (
    <div className="container my-5">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="moderate-container border rounded p-4 shadow">
            <div className="slide-container text-center">
              {currentSlideData.type === 'content' ? (
                // Content Slide
                <div className="slide content-slide">
                  <h2 className="mb-3">{concept.concept}</h2>
                  <div className="content-box">
                    <p>{concept.description}</p>
                  </div>
                </div>
              ) : (
                // Quiz Slide
                <div className="slide quiz-slide">
                  <h2 className="mb-3">Quiz for: {concept.concept}</h2>
                  <div className="question-box">
                    {quizzes[concept.concept] && quizzes[concept.concept].length > 0 ? (
                      quizzes[concept.concept].map((question, questionIndex) => (
                        <div key={questionIndex} className="quiz-question mb-4">
                          <p className="question-text font-weight-bold">{question.question}</p>
                          <div className="options">
                            {question.answer.split('\n').map((option, idx) => (
                              <div key={idx} className="form-check">
                                <label className="form-check-label option-label">
                                  <input
                                    type="radio"
                                    className="form-check-input"
                                    name={`${concept.concept}-${questionIndex}`}
                                    value={option}
                                    onChange={() => handleAnswerSelect(concept.concept, questionIndex, option)}
                                    checked={
                                      userAnswers[concept.concept] &&
                                      userAnswers[concept.concept][questionIndex] === option
                                    }
                                  />
                                  {option}
                                </label>
                              </div>
                            ))}
                          </div>
                          <button
                            className="btn btn-sm btn-info mt-2"
                            onClick={() => toggleSolution(concept.concept, questionIndex)}
                          >
                            {solutionVisible[concept.concept]?.[questionIndex] ? 'Hide Answer' : 'Check Answer'}
                          </button>
                          {solutionVisible[concept.concept]?.[questionIndex] && (
                            <div className="alert alert-secondary mt-2" role="alert">
                              Correct Answer: {question.answer.split('\n')[0]}
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <p>No quiz available for this concept.</p>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Navigation Buttons */}
            <div className="nav-buttons d-flex justify-content-between mt-4">
              {currentSlide > 0 && (
                <button className="btn btn-secondary nav-button" onClick={handlePrevious}>
                  Previous
                </button>
              )}
              <button className="btn btn-primary nav-button" onClick={handleNext}>
                {currentSlide === slides.length - 1 ? 'Submit and Proceed' : 'Next'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModerateLevel;