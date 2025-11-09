"use client";

import { useEffect, useState } from "react";
import ChartCard from "./components/ChartCard";
import DietDataTable from "./components/DietDataTable";
import DietInsightsTable from "./components/DietInsightsTable";
import Papa from "papaparse";

export default function Home() {
  const API_BASE =
    "https://diet-analysis-afb4ceacghajcsbp.canadacentral-01.azurewebsites.net/api/";

  const validDiets = ["Paleo", "Vegan", "Keto", "Mediterranean", "Dash", "All"];
  const [selectedDiet, setSelectedDiet] = useState("All");

  // Diet used for pie chart since we added the feature to select diet for pie chart separately
  const [pieDiet, setPieDiet] = useState("Keto");

  const [charts, setCharts] = useState({
    bar: { img: null, time: null },
    line: { img: null, time: null },
    pie: { img: null, time: null },
  });

  const [filteredData, setFilteredData] = useState([]);
  const [csvProcessingTime, setCsvProcessingTime] = useState(null);
  const [loadingData, setLoadingData] = useState(false);

  const fetchChart = async (type, endpoint) => {
    const start = performance.now();
    try {
      const response = await fetch(`${API_BASE}${endpoint}`);
      const blob = await response.blob();
      const imgUrl = URL.createObjectURL(blob);
      const elapsed = ((performance.now() - start) / 1000).toFixed(2);

      setCharts((prev) => ({
        ...prev,
        [type]: { img: imgUrl, time: elapsed },
      }));
    } catch (error) {
      console.error(`Error fetching ${type} chart:`, error);
    }
  };

  const fetchPieChart = async (diet) => {
    const start = performance.now();
    try {
      const response = await fetch(`${API_BASE}DietPieChart?diet=${diet}`);
      if (!response.ok) throw new Error(`Pie chart not found for diet: ${diet}`);
      const blob = await response.blob();
      const imgUrl = URL.createObjectURL(blob);
      const elapsed = ((performance.now() - start) / 1000).toFixed(2);

      setCharts((prev) => ({
        ...prev,
        pie: { img: imgUrl, time: elapsed },
      }));
    } catch (error) {
      console.error("Error fetching Pie chart:", error);
    }
  };

  // Fetch each chart on mount
  useEffect(() => {
    fetchChart("bar", "DietBarChart");
    fetchChart("line", "DietLineChart");
    fetchPieChart(pieDiet);
  }, []);

  useEffect(() => {
    fetchPieChart(pieDiet);
  }, [pieDiet]);

  // Gets the CSV data with the selected Diet
  const fetchDietData = async (diet) => {
    setLoadingData(true);
    const start = performance.now();
    try {
      const response = await fetch(`${API_BASE}DietSearch?diet=${diet}`);
      const csvText = await response.text();

      // Parse CSV with PapaParse
      const parsed = Papa.parse(csvText, {
        header: true,       // use first row as header
        skipEmptyLines: true
      });

      setFilteredData(parsed.data);

      // CSV processing time
      const elapsed = ((performance.now() - start) / 1000).toFixed(2);
      setCsvProcessingTime(elapsed);
    } catch (error) {
      console.error("Error fetching diet data:", error);
      setFilteredData([]);
      setCsvProcessingTime(null);
    } finally {
      setLoadingData(false);
    }
  };

  // Load all diets on mount
  useEffect(() => {
    fetchDietData("All");
  }, []);

  const handleDietChange = (diet) => {
    setSelectedDiet(diet);
    fetchDietData(diet);
  };

  return (
    <div>
      {/* Header */}
      <header className="bg-[#2563EB] text-white p-4 flex justify-between items-center sticky top-0 z-10">
        <h1 className="text-3xl font-bold">Nutritional Insights</h1>

        <button
          onClick={() => {
            setCharts({    
              bar: { img: null, time: null },
              line: { img: null, time: null },
              pie: { img: null, time: null },
            });
            setLoadingData(true);

            fetchChart("bar", "DietBarChart");
            fetchChart("line", "DietLineChart");
            setPieDiet("Keto");
            fetchPieChart(pieDiet);
            fetchDietData(selectedDiet);

            setLoadingData(false);
          }}
          className="px-4 py-2 bg-white text-blue-500 font-semibold rounded hover:bg-gray-100"
        >
          Refresh
        </button>
      </header>

      <main>
        {/* Charts */}
        <section className="py-6 px-10">
          <h2 className="text-xl font-semibold">Explore Nutritional Insights</h2>

          <div className="flex flex-wrap justify-between gap-6 p-4">
            {/* Bar Chart */}
            <ChartCard
              title="Bar Chart"
              desc="Average Protein Content by Diet Type"
              imgUrl={charts.bar.img}
              processingTime={charts.bar.time}
            />

            {/* Line Chart */}
            <ChartCard
              title="Line Chart"
              desc="Nutrient Trends Over Time"
              imgUrl={charts.line.img}
              processingTime={charts.line.time}
            />

            {/* Pie Chart */}
            <ChartCard
              title="Pie Chart"
              desc={`Macronutrient Composition for ${pieDiet} Diet`}
              imgUrl={charts.pie.img}
              processingTime={charts.pie.time}
            />
          </div>
        </section>

        {/* Nutritional Insights Button */}
        <section className="py-6 px-10">
          <h2 className="text-xl font-semibold">API Interactions</h2>
          <DietInsightsTable apiUrl={`${API_BASE}DietInsights`} />
        </section>

        {/* Filters and Data Interaction */}
        <section className="py-6 px-10">
          <h2 className="text-xl font-semibold">Filters and Data Interaction</h2>

          {/* Diet selectors: CSV table + Pie Chart */}
          <div className="mt-4 flex flex-wrap gap-4 items-center">
            {/* CSV Table Diet Selector */}
            <div className="flex items-center gap-2">
              <label className="font-medium" htmlFor="diet-select">
                Select Table Diet:
              </label>
              <select
                id="diet-select"
                value={selectedDiet}
                onChange={(e) => handleDietChange(e.target.value)}
                className="border border-gray-300 rounded p-2"
              >
                {validDiets.map((diet) => (
                  <option key={diet} value={diet}>
                    {diet}
                  </option>
                ))}
              </select>
            </div>

            {/* Pie Chart Diet Selector */}
            <div className="flex items-center gap-2">
              <label className="font-medium" htmlFor="pie-diet-select">
                Select Pie Chart Diet:
              </label>
              <select
                id="pie-diet-select"
                value={pieDiet}
                onChange={(e) => setPieDiet(e.target.value)}
                className="border border-gray-300 rounded p-2"
              >
                {validDiets
                  .filter((d) => d !== "All") // Pie chart requires a single diet
                  .map((diet) => (
                    <option key={diet} value={diet}>
                      {diet}
                    </option>
                  ))}
              </select>
            </div>
          </div>

          {/* Diet CSV Table with Pagination */}
          <DietDataTable
            data={filteredData}
            loading={loadingData}
            processingTime={csvProcessingTime}
            selectedDiet={selectedDiet}
          />
        </section>
      </main>
      <footer className="bg-[#2563EB] text-white p-4 flex justify-center items-center">
        <p>© 2025 Nutritional Insights. All Rights Reserved.</p>
      </footer>
    </div>
  );
}
