import React from "react";
import MapView from "./components/MapView";
import ReportsTable from "./components/ReportsTable";
import UploadForm from "./components/UploadForm";

function App() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-center mb-6 text-blue-700">Smart Pavers Dashboard</h1>
      <div className="grid md:grid-cols-2 gap-6">
        <MapView />
        <UploadForm />
      </div>
      <div className="mt-8">
        <ReportsTable />
      </div>
    </div>
  );
}

export default App;
