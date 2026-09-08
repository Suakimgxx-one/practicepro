import { Route, Routes } from "react-router-dom";
import { PiecesListPage } from "@/pages/PiecesListPage";
import { PieceDetailPage } from "@/pages/PieceDetailPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<PiecesListPage />} />
      <Route path="/pieces/:pieceId" element={<PieceDetailPage />} />
    </Routes>
  );
}

export default App;
