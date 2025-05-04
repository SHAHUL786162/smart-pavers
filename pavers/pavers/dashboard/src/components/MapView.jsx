import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useState, useEffect } from "react";
import axios from "axios";
import L from "leaflet";

function MapView() {
  const [reports, setReports] = useState([]);

  useEffect(() => {
    fetchReports();
    const interval = setInterval(fetchReports, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchReports = async () => {
    try {
      const res = await axios.get("http://localhost:5000/reports");
      setReports(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const icon = new L.Icon({
    iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
  });

  return (
    <MapContainer center={[12.9721, 77.5933]} zoom={12} className="h-96 w-full rounded-lg shadow-md">
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {reports.map((report) => (
        <Marker key={report.id} position={[report.latitude, report.longitude]} icon={icon}>
          <Popup>
            <strong>{report.type}</strong> <br />
            Severity: {report.severity} <br />
            Priority: {report.priority}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}

export default MapView;
