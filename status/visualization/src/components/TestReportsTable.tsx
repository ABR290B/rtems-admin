import React from 'react';

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

interface TestReportsTableProps {
  data: TestReport[];
}

const TestReportsTable: React.FC<TestReportsTableProps> = ({ data }) => {
  return (
    <section className="table-section">
      <table>
        <thead>
          <tr>
            <th>Host</th>
            <th>Passed Count</th>
            <th>Failed Count</th>
            <th>User Input Count</th>
            <th>Expected Fail Count</th>
            <th>Indeterminate</th>
            <th>Benchmark</th>
            <th>Timeout</th>
            <th>Invalid</th>
            <th>Wrong Version</th>
            <th>Wrong Build</th>
            <th>Wrong Tools</th>
            {/* ... Other headers */}
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index}>
              <td>{item.Host}</td>
              <td>{item['Passed Count']}</td>
              <td>{item['Failed Count']}</td>
              <td>{item['User Input Count']}</td>
              <td>{item['Expectd Fail Count']}</td>
              <td>{item['Indeterminate Count']}</td>
              <td>{item['Benchmark Count']}</td>
              <td>{item['Timeout Count']}</td>
              <td>{item['Invalid Count']}</td>
              <td>{item['Wrong Version Count']}</td>
              <td>{item['Wrong Build Count']}</td>
              <td>{item['Wrong Tools Count']}</td>
              {/* ... Other cells */}
            </tr>
          ))}
        </tbody>
      </table>
      {/* ... Pagination */}
    </section>
  );
};

export default TestReportsTable;
