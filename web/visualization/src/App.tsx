import React, { useState } from 'react';
import './App.css';

const sampleData = [
  {
    Date: 'Sat, 21 Jan 2023',
    Result: 'PASSED',
    OS: 'x86_64-linux-gnu',
    Arch: 'rtems-moxie',
    Release: '6',
  },
  {
    Date: 'Sat, 22 Jan 2023',
    Result: 'PASSED',
    OS: 'x86_64-linux-gnu',
    Arch: 'rtems-nios2',
    Release: '6',
  },
];

const App: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  const filteredData = sampleData.filter((data) =>
    Object.values(data).some((value) =>
      value.toString().toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  return (
    <div className="container">
      <h1 className="title">Month Build Summary</h1>
      <input
        type="text"
        placeholder="Search..."
        value={searchQuery}
        onChange={handleSearch}
        className="search-input"
      />
      <table className="table">
        <thead>
          <tr>
            <th>Date</th>
            <th>OS</th>
            <th>Arch</th>
            <th>Release</th>
            <th>Result</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          {filteredData.map((data, index) => (
            <tr key={index}>
              <td>{data.Date}</td>
              <td>{data.OS}</td>
              <td>{data.Arch}</td>
              <td>{data.Release}</td>
              <td>{data.Result}</td>
              <td>
                <a href="#" className="link">Link</a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default App;