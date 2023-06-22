// Define an interface to match the structure of the JSON data
interface SummaryData {
  year: string;
  data: SummaryRow[];
}

// Define an interface to match the structure of each summary row
interface SummaryRow {
  Month: string;
  Passes: number;
  Fails: number;
}

// Function to fetch the JSON data and populate the table
async function populateTable() {
  const cacheBuster = new Date().getTime(); // Generate a timestamp as the cache-buster
  const url = `summary_table.json?cache=${cacheBuster}`; // Append the cache-buster parameter to the URL

  const response = await fetch(url);
  const data: SummaryData[] = await response.json();

  const tableBody = document.querySelector('#summary-table tbody');
  if (!tableBody) return;

  const yearDropdown = document.querySelector('#year-dropdown') as HTMLSelectElement;
  if (!yearDropdown) return;

  yearDropdown.addEventListener('change', (event) => {
    const selectedYear = (event.target as HTMLSelectElement).value;
    const selectedData = data.find((item) => item.year === selectedYear)?.data || [];

    tableBody.innerHTML = ''; // Clear the existing table rows

    selectedData.forEach((row) => {
      const tableRow = document.createElement('tr');
      tableRow.innerHTML = `
        <td>${row.Month}</td>
        <td>${row.Passes}</td>
        <td>${row.Fails}</td>
      `;
      tableBody.appendChild(tableRow);
    });
  });

  // Generate the year dropdown options based on the available years in the JSON data
  const years = data.map((item) => item.year);
  years.forEach((year) => {
    const option = document.createElement('option');
    option.value = year;
    option.textContent = year;
    yearDropdown.appendChild(option);
  });

  // Initial population of the table with the data of the first available year
  if (years.length > 0) {
    const firstYear = years[0];
    const firstYearData = data.find((item) => item.year === firstYear)?.data || [];
    firstYearData.forEach((row) => {
      const tableRow = document.createElement('tr');
      tableRow.innerHTML = `
        <td>${row.Month}</td>
        <td>${row.Passes}</td>
        <td>${row.Fails}</td>
      `;
      tableBody.appendChild(tableRow);
    });
  }
}

// Call the populateTable function when the DOM is loaded
document.addEventListener('DOMContentLoaded', populateTable);
