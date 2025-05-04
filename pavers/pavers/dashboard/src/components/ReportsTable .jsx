import { useState, useEffect } from "react";
import axios from "axios";

function ReportsTable() {
  const [reports, setReports] = useState([]);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const res = await axios.get("http://localhost:5000/reports");
      setReports(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Defect Reports</h2>
      <table className="w-full table-auto">
        <thead>
          <tr className="bg-gray-200">
            <th className="p-2">Type</th>
            <th className="p-2">Severity</th>
            <th className="p-2">Priority</th>
            <th className="p-2">Location</th>
            <th className="p-2">Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((report) => (
            <tr key={report.id} className="text-center">
              <td className="p-2">{report.type}</td>
              <td className="p-2">{report.severity}</td>
              <td className="p-2 font-bold text-red-500">{report.priority}</td>
              <td className="p-2">{report.latitude.toFixed(4)}, {report.longitude.toFixed(4)}</td>
              <td className="p-2">{new Date(report.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ReportsTable;
