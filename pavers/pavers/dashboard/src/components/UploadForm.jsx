import { useState } from "react";
import axios from "axios";

function UploadForm() {
  const [file, setFile] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("image", file);

    try {
      await axios.post("http://localhost:5000/report", formData);
      alert("✅ File uploaded and processed successfully!");
      window.location.reload();
    } catch (err) {
      console.error(err);
      alert("❌ Upload failed. Try again.");
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Upload Defect Image</h2>
      <form onSubmit={handleUpload} className="flex flex-col gap-4">
        <input
          type="file"
          accept="image/*,video/*"
          onChange={(e) => setFile(e.target.files[0])}
          className="p-2 border rounded"
          required
        />
        <button type="submit" className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded">
          Upload
        </button>
      </form>
    </div>
  );
}

export default UploadForm;
