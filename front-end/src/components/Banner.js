import React from 'react';
import './Banner.css';

function Banner({ username, wholeName }) {
  return (
    <div className="banner">
      <h1>{username} - {wholeName || 'Loading...'}</h1>
    </div>
  );
}

export default Banner;
