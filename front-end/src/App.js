import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './App.css';
import Banner from './components/Banner';
import MyButton from './components/MyButton';
import DatePicker from './components/DatePicker';

function App() {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [downloadMessage, setDownloadMessage] = useState('');
  const [wholeName, setWholeName] = useState('');
  const [tollStations, setTollStations] = useState([]);
  const [selectedTollStation, setSelectedTollStation] = useState('');

  const username = localStorage.getItem('username');
  const navigate = useNavigate();

  // Determine if the user is admin
  const isAdmin = username === 'admin';

  // Redirect to login if no username is found
  useEffect(() => {
    if (!username) {
      navigate('/');
    }
  }, [username, navigate]);

  // Fetch user information including operator name
  useEffect(() => {
    const fetchUserInfo = async () => {
      try {
        const response = await fetch('http://localhost:9115/api/user-info', {
          headers: {
            'X-OBSERVATORY-AUTH': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setWholeName(data.operator);
        }
      } catch (error) {
        console.error('Error fetching user info:', error);
      }
    };

    if (username) {
      fetchUserInfo();
    }
  }, [username]);

  // Fetch Toll Stations from the API
  useEffect(() => {
    const fetchStations = async () => {
      try {
        const response = await fetch('http://localhost:9115/api/tollstations', {
          headers: {
            'X-OBSERVATORY-AUTH': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (!response.ok) throw new Error('Failed to fetch stations');

        const data = await response.json();
        
        let stations = [];
        if (Array.isArray(data)) {
          stations = data;
        } else if (data?.stations) {
          stations = data.stations;
        }

        const filteredStations = stations

        setTollStations(filteredStations);
      } catch (error) {
        console.error('Error fetching stations:', error);
        if (error.message.includes('401')) {
          localStorage.removeItem('token');
          localStorage.removeItem('username');
          navigate('/');
        }
      }
    };

    fetchStations();
  }, [username, isAdmin, navigate]);

  // Download handler
  const handleDownload = async (format) => {
    if (!startDate || !endDate || startDate > endDate || !selectedTollStation) {
      setDownloadMessage('Παρακαλώ συμπληρώστε όλα τα πεδία.');
      return;
    }

    try {
      const formattedStart = startDate.replace(/-/g, '');
      const formattedEnd = endDate.replace(/-/g, '');
      const url = `http://localhost:9115/api/tollStationPasses/${selectedTollStation}/${formattedStart}/${formattedEnd}?format=${format}`;

      const response = await fetch(url, {
        headers: {
          'X-OBSERVATORY-AUTH': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) throw new Error('Αποτυχία λήψης δεδομένων');

      // Handle file download
      const blob = await response.blob();
      const filename = `${username}_${selectedTollStation}_${formattedStart}-${formattedEnd}.${format}`;
      
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setDownloadMessage(`Λήψη ${format.toUpperCase()} ξεκίνησε...`);
      setTimeout(() => setDownloadMessage(''), 5000);

    } catch (error) {
      console.error('Download error:', error);
      setDownloadMessage('Σφάλμα κατά τη λήψη: ' + error.message);
    }
  };

  return (
    <div className="App">
      <Banner username={username} wholeName={wholeName} />
      <h1>Επιλέξτε το χρονικό διάστημα</h1>

      <div className="input-group">
        <DatePicker 
          label="Ημερομηνία Έναρξης"
          value={startDate}
          onChange={setStartDate}
        />
        <DatePicker
          label="Ημερομηνία Λήξης"
          value={endDate}
          onChange={setEndDate}
        />
      </div>

      <div className="station-select">
        <label>Σταθμός Διοδίων:</label>
        <select
          value={selectedTollStation}
          onChange={(e) => setSelectedTollStation(e.target.value)}
          required
        >
          <option value="">Επιλέξτε σταθμό...</option>
          {tollStations.map(station => (
            <option key={station.TollID} value={station.TollID}>
              {station.name} ({station.TollID})
            </option>
          ))}
        </select>
      </div>

      <div className="download-buttons">
        <MyButton 
          onClick={() => handleDownload('csv')}
          label="Λήψη CSV"
          icon="📄"
        />
        <MyButton
          onClick={() => handleDownload('json')}
          label="Λήψη JSON"
          icon="📑"
        />
      </div>

      {downloadMessage && (
        <div className="download-status">
          {downloadMessage}
        </div>
      )}
    </div>
  );
}

export default App;