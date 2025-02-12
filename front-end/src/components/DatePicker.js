import React from 'react';

function DatePicker({ label, value, onChange }) {
  return (
    <div style={{ margin: '20px' }}>
      <label>{label}:</label>
      <input type="date" value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}

export default DatePicker;
