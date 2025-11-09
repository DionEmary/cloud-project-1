"use client";

import { useState, useEffect } from "react";

export default function ChartCard({ title, desc, imgUrl, processingTime }) {
  const [loaded, setLoaded] = useState(false);

  // Reset loaded state whenever imgUrl changes
  useEffect(() => {
    setLoaded(false);
  }, [imgUrl]);

  return (
    <div className="bg-white drop-shadow-2xl rounded-lg p-6 flex-1 min-w-[300px]">
      <h3 className="text-lg font-medium">{title}</h3>

      {!imgUrl || !loaded ? (
        <p className="text-gray-500 mt-4">Loading chart...</p>
      ) : (
        <p className="mt-2">
          {desc} | Processed in {processingTime}s
        </p>
      )}

      {imgUrl && (
        <img
          src={imgUrl}
          alt={title}
          className="mt-4 rounded-lg w-full"
          onLoad={() => setLoaded(true)}
        />
      )}
    </div>
  );
}
