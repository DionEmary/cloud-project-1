"use client";

import { useState } from "react";

export default function DietInsightsTable({ apiUrl }) {
  const [insightsData, setInsightsData] = useState([]);
  const [processingTime, setProcessingTime] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchInsights = async () => {
    setLoading(true);
    const start = performance.now();
    try {
      const response = await fetch(apiUrl);
      const json = await response.json();

      // API returns { elapsed_seconds, diet_insights }
      setInsightsData(json.diet_insights);
      setProcessingTime(((performance.now() - start) / 1000).toFixed(2));
    } catch (error) {
      console.error("Error fetching diet insights:", error);
      setInsightsData([]);
      setProcessingTime(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="my-6">
      <button
        onClick={fetchInsights}
        className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
      >
        Gain Nutritional Insights
      </button>

      {loading && <p className="text-gray-500 mt-2">Loading insights...</p>}

      {insightsData.length > 0 && (
        <div className="mt-4 overflow-x-auto">
          <p className="mb-2 text-gray-700">
            Nutritional Insights | Processed in {processingTime}s
          </p>
          <table className="min-w-full border border-gray-200">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-4 py-2 border-b">Diet</th>
                {Object.keys(insightsData[0])
                  .filter((k) => k !== "Diet_type")
                  .map((macro) => (
                    <th key={macro} className="px-4 py-2 border-b">
                      {macro}
                    </th>
                  ))}
              </tr>
            </thead>
            <tbody>
              {insightsData.map((row, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-2 border-b">{row.Diet_type}</td>
                  {Object.keys(row)
                    .filter((k) => k !== "Diet_type")
                    .map((macro, i) => (
                      <td key={i} className="px-4 py-2 border-b">
                        {row[macro].toFixed(2)}
                      </td>
                    ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
