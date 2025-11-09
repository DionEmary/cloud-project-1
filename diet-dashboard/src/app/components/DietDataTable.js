"use client";

import { useState } from "react";

export default function DietDataTable({
  data,
  loading,
  processingTime,
  selectedDiet,
  rowsPerPage = 25,
}) {
  const [currentPage, setCurrentPage] = useState(1);

  if (!data || data.length === 0) return null;

  const totalPages = Math.ceil(data.length / rowsPerPage);
  const currentRows = data.slice(
    (currentPage - 1) * rowsPerPage,
    currentPage * rowsPerPage
  );

  const goToPage = (page) => {
    if (page < 1 || page > totalPages) return;
    setCurrentPage(page);
  };

  // Condensed pagination numbers
  const getPageNumbers = (current, total, maxVisible = 6) => {
    const pages = [];
    if (total <= maxVisible) {
      for (let i = 1; i <= total; i++) pages.push(i);
    } else {
      let start = Math.max(current - Math.floor(maxVisible / 2), 1);
      let end = start + maxVisible - 1;
      if (end > total) {
        end = total;
        start = end - maxVisible + 1;
      }
      for (let i = start; i <= end; i++) pages.push(i);
    }
    return pages;
  };

  // Function to export CSV
  const exportToCSV = () => {
    if (!data || data.length === 0) return;

    const keys = Object.keys(data[0]);

    const csvRows = [
      keys.join(","), // header row
      ...data.map((row) =>
        keys
          .map((key) => {
            const val = row[key]?.toString() ?? "";
            // Escape quotes and wrap in quotes if it contains comma, quote, or newline
            if (val.includes(",") || val.includes('"') || val.includes("\n")) {
              return `"${val.replace(/"/g, '""')}"`;
            }
            return val;
          })
          .join(",")
      ),
    ];

    const csvString = csvRows.join("\n");
    const blob = new Blob([csvString], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.setAttribute("download", `${selectedDiet}_diet_data.csv`);
    link.click();
  };

  return (
    <div className="mt-6">
      {loading ? (
        <p className="text-gray-500">Loading data...</p>
      ) : data.length === 0 ? (
        <p className="text-gray-500 mt-2">No data to display.</p>
      ) : (
        <>
          <div className="flex justify-between items-center mb-2">
            <p className="text-gray-700">
              {selectedDiet} Diet Data | Processed in {processingTime}s
            </p>
            <button
              onClick={exportToCSV}
              className="px-3 py-1 border rounded bg-blue-500 text-white hover:bg-blue-600"
            >
              Download CSV
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full border border-gray-200">
              <thead>
                <tr className="bg-gray-100">
                  {Object.keys(currentRows[0]).map((col) => (
                    <th
                      key={col}
                      className="px-4 py-2 text-left border-b border-gray-200"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {currentRows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    {Object.values(row).map((val, i) => (
                      <td
                        key={i}
                        className="px-4 py-2 border-b border-gray-200"
                      >
                        {val}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex justify-center items-center mt-4 space-x-2">
            <button
              onClick={() => goToPage(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Previous
            </button>

            {getPageNumbers(currentPage, totalPages).map((page) => (
              <button
                key={page}
                onClick={() => goToPage(page)}
                className={`px-3 py-1 border rounded ${
                  page === currentPage ? "bg-blue-500 text-white" : ""
                }`}
              >
                {page}
              </button>
            ))}

            {totalPages > 6 && (
              <button
                onClick={() => {
                  const input = prompt("Enter page number:");
                  const pageNum = Number(input);
                  if (pageNum >= 1 && pageNum <= totalPages) goToPage(pageNum);
                }}
                className="px-3 py-1 border rounded"
              >
                ...
              </button>
            )}

            <button
              onClick={() => goToPage(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
