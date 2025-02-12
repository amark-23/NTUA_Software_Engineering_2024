import Papa from 'papaparse';

export function parseCSV(file, setCsvData) {
  Papa.parse(file, {
    complete: (result) => setCsvData(result.data),
    header: true,
  });
}

// utils/csvUtils.js

export function filterCSVData(data, startDate, endDate, tollID) {
    return data.filter(row => {
      const timestamp = row.timestamp.split(' ')[0]; // Extract just the date
      return (
        timestamp >= startDate &&
        timestamp <= endDate &&
        row.tollID === tollID // Match only the selected TollID
      );
    });
  }

