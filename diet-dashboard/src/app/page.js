"use client";

import { useEffect, useState } from "react";
import ChartCard from "./components/ChartCard";
import DietDataTable from "./components/DietDataTable";
import DietInsightsTable from "./components/DietInsightsTable";
import UserMenu from "./components/UserMenu";
import ProtectedRoute from "./components/ProtectedRoute";

function HomeContent() {
  const API_BASE =
    "https://project-3-backend-brayevbje4cxhsek.canadacentral-01.azurewebsites.net/api/";

  const validDiets = ["Paleo", "Vegan", "Keto", "Mediterranean", "Dash", "All"];
  const [selectedDiet, setSelectedDiet] = useState("All");
  const [pieDiet, setPieDiet] = useState("Keto");
  const [keyword, setKeyword] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);

  const [charts, setCharts] = useState({
    bar: { img: null, time: null },
    line: { img: null, time: null },
    pie: { img: null, time: null },
  });

  const [filteredData, setFilteredData] = useState([]);
  const [pagination, setPagination] = useState({});
  const [loadingData, setLoadingData] = useState(false);

  // Fetch charts
  const fetchChart = async (type, endpoint) => {
    const start = performance.now();
    try {
      const response = await fetch(`${API_BASE}${endpoint}`);
      const blob = await response.blob();
      const imgUrl = URL.createObjectURL(blob);
      const elapsed = ((performance.now() - start) / 1000).toFixed(2);

      setCharts((prev) => ({ ...prev, [type]: { img: imgUrl, time: elapsed } }));
    } catch (err) {
      console.error(`Error fetching ${type} chart:`, err);
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

      setCharts((prev) => ({ ...prev, pie: { img: imgUrl, time: elapsed } }));
    } catch (err) {
      console.error("Error fetching Pie chart:", err);
    }
  };

  // Fetch diet table
  const fetchDietData = async (diet = selectedDiet, kw = keyword, pg = page) => {
    setLoadingData(true);
    try {
      const params = new URLSearchParams({
        diet: diet,
        keyword: kw,
        page: pg,
        page_size: pageSize,
      });
      const response = await fetch(`${API_BASE}DietSearch?${params}`);
      if (!response.ok) throw new Error(`Error fetching data: ${response.statusText}`);
      const json = await response.json();
      setFilteredData(json.data);
      setPagination(json.pagination);
    } catch (err) {
      console.error(err);
      setFilteredData([]);
      setPagination({});
    } finally {
      setLoadingData(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchChart("bar", "DietBarChart");
    fetchChart("line", "DietLineChart");
    fetchPieChart(pieDiet);
    fetchDietData("All");
  }, []);

  // Refetch pie chart when pieDiet changes
  useEffect(() => {
    fetchPieChart(pieDiet);
  }, [pieDiet]);

  // Refetch table when selectedDiet, page, or keyword changes
  useEffect(() => {
    fetchDietData(selectedDiet, keyword, page);
  }, [selectedDiet, page, keyword]);

  const handleDietChange = (diet) => {
    setSelectedDiet(diet);
    setPage(1); // reset to first page
  };

  return (
    <div>
      {/* Header */}
      <header className="bg-[#2563EB] text-white p-4 flex justify-between items-center sticky top-0 z-10">
        <h1 className="text-3xl font-bold">Nutritional Insights</h1>
        <div className="flex items-center gap-4">
          <UserMenu />
          <button
            onClick={() => {
              setCharts({ bar: { img: null }, line: { img: null }, pie: { img: null } });
              fetchChart("bar", "DietBarChart");
              fetchChart("line", "DietLineChart");
              fetchPieChart(pieDiet);
              fetchDietData(selectedDiet);
            }}
            className="px-4 py-2 bg-white text-blue-500 font-semibold rounded hover:bg-gray-100"
          >
            Refresh
          </button>
        </div>
      </header>

      <main>
        {/* Charts */}
        <section className="py-6 px-10">
          <h2 className="text-xl font-semibold">Explore Nutritional Insights</h2>
          <div className="flex flex-wrap justify-between gap-6 p-4">
            <ChartCard
              title="Bar Chart"
              desc="Average Protein Content by Diet Type"
              imgUrl={charts.bar.img}
              processingTime={charts.bar.time}
            />
            <ChartCard
              title="Line Chart"
              desc="Nutrient's Per Diet comparison"
              imgUrl={charts.line.img}
              processingTime={charts.line.time}
            />
            <ChartCard
              title="Pie Chart"
              desc={`Macronutrient Composition for ${pieDiet} Diet`}
              imgUrl={charts.pie.img}
              processingTime={charts.pie.time}
            />
          </div>
        </section>

        {/* Insights */}
        <section className="py-6 px-10">
          <h2 className="text-xl font-semibold">API Interactions</h2>
          <DietInsightsTable apiUrl={`${API_BASE}DietInsights`} />
        </section>

        {/* Filters and Table */}
        <section className="py-6 px-10">
          <h2 className="text-xl font-semibold">Filters and Data Interaction</h2>
          <div className="mt-4 flex flex-wrap gap-4 items-center">
            {/* Diet selector */}
            <div className="flex items-center gap-2">
              <label className="font-medium" htmlFor="diet-select">Table Diet:</label>
              <select
                id="diet-select"
                value={selectedDiet}
                onChange={(e) => handleDietChange(e.target.value)}
                className="border border-gray-300 rounded p-2"
              >
                {validDiets.map((diet) => <option key={diet} value={diet}>{diet}</option>)}
              </select>
            </div>

            {/* Keyword search */}
            <div className="flex items-center gap-2">
              <label className="font-medium" htmlFor="keyword">Search:</label>
              <input
                id="keyword"
                type="text"
                value={keyword}
                onChange={(e) => { setKeyword(e.target.value); setPage(1); }}
                placeholder="Enter keyword..."
                className="border p-2 rounded"
              />
            </div>

            {/* Pie Chart selector */}
            <div className="flex items-center gap-2">
              <label className="font-medium" htmlFor="pie-diet-select">Pie Chart Diet:</label>
              <select
                id="pie-diet-select"
                value={pieDiet}
                onChange={(e) => setPieDiet(e.target.value)}
                className="border border-gray-300 rounded p-2"
              >
                {validDiets.filter(d => d !== "All").map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
          </div>

          <DietDataTable
            data={filteredData}
            loading={loadingData}
            currentPage={pagination.current_page || 1}
            totalPages={pagination.total_pages || 1}
            onPageChange={setPage}
          />
        </section>
      </main>

      <footer className="bg-[#2563EB] text-white p-4 flex justify-center items-center">
        <p>© 2025 Nutritional Insights. All Rights Reserved.</p>
      </footer>
    </div>
  );
}

export default function Home() {
  return (
    <ProtectedRoute>
      <HomeContent />
    </ProtectedRoute>
  );
}
