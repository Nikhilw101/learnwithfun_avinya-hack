import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import TestPage from './TestPage';

const Dashboard = () => {
  const [userId, setUserId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const storedUserId = localStorage.getItem('user_id');
    if (!storedUserId) {
      // Redirect to login page if no user_id in localStorage
      navigate('/login');
    } else {
      setUserId(storedUserId); // Set the userId if it exists
    }
  }, [navigate]);

  return (
    <div className="dashboard-container">
      {userId ? (
        <h2>Welcome to your Dashboard, User ID: {userId}</h2>
      ) : (
        <p>Loading...</p>
      )}

      <TestPage/>
    </div>
  );
};

export default Dashboard;
