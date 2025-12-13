"use client";

import { useState } from "react";

export default function DietDataTable({
  data,
  loading,
  currentPage = 1,
  totalPages = 1,
  onPageChange = () => {},
}) {
  const [inputPage, setInputPage] = useState("");

  if (!data || data.length === 0) return null;

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

  const handleInputPage = () => {
    const pageNum = Number(inputPage);
    if (!isNaN(pageNum) && pageNum >= 1 && pageNum <= totalPages) {
      onPageChange(pageNum);
      setInputPage("");
    }
  };

  return (
    <div className="mt-6">
      {loading ? (
        <p className="text-gray-500">Loading data...</p>
      ) : data.length === 0 ? (
        <p className="text-gray-500 mt-2">No data to display.</p>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="min-w-full border border-gray-200">
              <thead>
                <tr className="bg-gray-100">
                  {Object.keys(data[0]).map((col) => (
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
                {data.map((row, idx) => (
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
          <div className="flex flex-wrap items-center justify-center mt-4 gap-2">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Previous
            </button>

            {getPageNumbers(currentPage, totalPages).map((page) => (
              <button
                key={page}
                onClick={() => onPageChange(page)}
                className={`px-3 py-1 border rounded ${
                  page === currentPage ? "bg-blue-500 text-white" : ""
                }`}
              >
                {page}
              </button>
            ))}

            <button
              onClick={() => {
                const input = prompt("Enter page number:");
                const pageNum = Number(input);
                if (!isNaN(pageNum) && pageNum >= 1 && pageNum <= totalPages)
                  onPageChange(pageNum);
              }}
              className="px-3 py-1 border rounded"
            >
              ...
            </button>

            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Next
            </button>

            {/* Direct page input */}
            <div className="flex items-center gap-1 ml-4">
              <input
                type="number"
                placeholder="Page"
                value={inputPage}
                onChange={(e) => setInputPage(e.target.value)}
                className="border rounded p-1 w-16 text-center"
                min={1}
                max={totalPages}
              />
              <button
                onClick={handleInputPage}
                className="px-2 py-1 bg-blue-500 text-white rounded"
              >
                Go
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
