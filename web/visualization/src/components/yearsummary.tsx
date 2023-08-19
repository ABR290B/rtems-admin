import React, { useState, useEffect } from 'react';


interface MonthlySummary {
  Month: string;
  ToolPasses: number;
  ToolFailures: number;
  // You can add more summary fields here as needed
}

const YearSummaryPage: React.FC = () => {
  const [monthlySummaries, setMonthlySummaries] = useState<MonthlySummary[]>([]);

  useEffect(() => {
    // Fetch your data and calculate monthly summaries here
    const fetchData = async () => {
      try {
        // Fetch and process data from your API or JSON file
        const response = await fetch('data/yearly_summary.json'); // Update with correct path
        const data = await response.json();
        
        // Calculate monthly summaries
        const summaries: MonthlySummary[] = data.map((monthData: any) => ({
          Month: monthData.Month,
          ToolPasses: monthData.ToolPasses,
          ToolFailures: monthData.ToolFailures,
          // Add more fields as needed
        }));
        
        setMonthlySummaries(summaries);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="year-summary-page">
      <h1 className="page-heading">Yearly Summary</h1>
      <table className="summary-table">
        <thead>
          <tr>
            <th>Month</th>
            <th>Tool Passes</th>
            <th>Tool Failures</th>
            {/* Add more header columns as needed */}
          </tr>
        </thead>
        <tbody>
          {monthlySummaries.map((summary, index) => (
            <tr key={index}>
              <td>{summary.Month}</td>
              <td>{summary.ToolPasses}</td>
              <td>{summary.ToolFailures}</td>
              {/* Add more data columns as needed */}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default YearSummaryPage;
