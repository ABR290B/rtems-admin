import React, { useState, useEffect } from 'react';
import '../styles/App.css';
import TestReportsTable from './TestReportsTable';

interface TestReport {
    Host: string;
    'Passed Count': number;
    'Failed Count': number;
    'User Input Count': number;
    'Expectd Fail Count': number;
    'Indeterminate Count': number;
    'Benchmark Count': number;
    'Timeout Count': number;
    'Invalid Count': number;
    'Wrong Version Count': number;
    'Wrong Build Count': number;
    'Wrong Tools Count': number;
}

const TestReportsPage: React.FC = () => {
  const [data, setData] = useState<TestReport[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('data/test_report.json'); // Update with the correct path to your JSON file
        const jsonData = await response.json();
        setData(jsonData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="app">
      <section className="top-section">
        <div className="logo-container">
          <img src="/rtemsorg300x300.png" alt="RTEMS Logo" />
        </div>
        <div className="title-container">
          <h1 className="main-heading">Test Reports</h1>
          <h2 className="sub-heading">January 2023</h2>
        </div>
        {/* ... Search input */}
      </section>
      <TestReportsTable data={data} />
      <footer className="footer">
        <p>© 1988-2023 RTEMS Project and contributors</p>
      </footer>
    </div>
  );
};

export default TestReportsPage;
