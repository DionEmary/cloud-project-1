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

  return (
    <div className="mt-6">
      {loading ? (
        <p className="text-gray-500">Loading data...</p>
      ) : data.length === 0 ? (
        <p className="text-gray-500 mt-2">No data to display.</p>
      ) : (
        <>
          <p className="mb-2 text-gray-700">
            {selectedDiet} Diet Data | Processed in {processingTime}s
          </p>

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
