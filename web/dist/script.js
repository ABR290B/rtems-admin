"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
// Function to fetch the JSON data and populate the table
function populateTable() {
    var _a;
    return __awaiter(this, void 0, void 0, function* () {
        const cacheBuster = new Date().getTime(); // Generate a timestamp as the cache-buster
        const url = `../summary_table.json?cache=${cacheBuster}`; // Append the cache-buster parameter to the URL
        const response = yield fetch(url);
        const data = yield response.json();
        const tableBody = document.querySelector('#summary-table tbody');
        if (!tableBody)
            return;
        const yearDropdown = document.querySelector('#year-dropdown');
        if (!yearDropdown)
            return;
        yearDropdown.addEventListener('change', (event) => {
            var _a;
            const selectedYear = event.target.value;
            const selectedData = ((_a = data.find((item) => item.year === selectedYear)) === null || _a === void 0 ? void 0 : _a.data) || [];
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
            const firstYearData = ((_a = data.find((item) => item.year === firstYear)) === null || _a === void 0 ? void 0 : _a.data) || [];
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
    });
}
// Call the populateTable function when the DOM is loaded
document.addEventListener('DOMContentLoaded', populateTable);
