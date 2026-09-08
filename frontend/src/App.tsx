import { Route, Routes } from "react-router-dom";
import { DashboardPage } from "@/pages/DashboardPage";
import { PiecesListPage } from "@/pages/PiecesListPage";
import { PieceDetailPage } from "@/pages/PieceDetailPage";
import { SettingsPage } from "@/pages/SettingsPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/pieces" element={<PiecesListPage />} />
      <Route path="/pieces/:pieceId" element={<PieceDetailPage />} />
      <Route path="/settings" element={<SettingsPage />} />
    </Routes>
  );
}

export default App;
