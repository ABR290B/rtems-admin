import React, { useState, useEffect } from 'react';
import '../styles/App.css';
import TestReportsPage from './TestReportsPage';
import YearSummaryPage from './yearsummary';

interface DataItem {
  Date: string;
  OS: string;
  Arch: string;
  Release: string;
  Result: string;
}

const App: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [data, setData] = useState<DataItem[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 50;

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('data/month_tool_build_report.json'); // Update with the correct path to your JSON file
        const jsonData = await response.json();
        setData(jsonData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  const filteredData = data.filter((item) =>
    Object.values(item).some((value) =>
      value.toString().toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredData.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);

  const handleNextPage = () => {
    setCurrentPage((prevPage) => prevPage + 1);
  };

  const handlePrevPage = () => {
    setCurrentPage((prevPage) => prevPage - 1);
  };

  return (
    <div className="app">
      <section className="top-section">
        <div className="logo-container">
          <img src="/rtemsorg300x300.png" alt="RTEMS Logo" />
        </div>
        <div className="title-container">
          <h1 className="main-heading">Monthly Build Summary</h1>
          <h2 className="sub-heading">January 2023</h2>
        </div>
        <div className="search-container">
          <label htmlFor="searchInput" className="search-label">
            Filter Search:
          </label>
          <input
            type="text"
            id="searchInput"
            placeholder="Search..."
            value={searchQuery}
            onChange={handleSearch}
          />
        </div>
      </section>

      <section className="table-section">
        <table>
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
            {currentItems.map((item, index) => (
              <tr key={index}>
                <td>{item.Date}</td>
                <td>{item.OS}</td>
                <td>{item.Arch}</td>
                <td>{item.Release}</td>
                <td style={{ backgroundColor: item.Result === "PASSED" ? "#84FFA7" : "#FF8484" }}>
                {item.Result}
                </td>
                <td>
                  <a href="#">Link</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="pagination-container">
          <button
            className="pagination-btn"
            onClick={handlePrevPage}
            disabled={currentPage === 1}
          >
            Previous Page
          </button>
          <span className="page-number">{`${currentPage}/${totalPages}`}</span>
          <button
            className="pagination-btn"
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
          >
            Next Page
          </button>
        </div>
      </section>

      <footer className="footer">
        <p>© 1988-2023 RTEMS Project and contributors</p>
      </footer>
    </div>
  );
};

export default App;
