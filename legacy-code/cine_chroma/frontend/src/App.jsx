import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";

export default function App() {
  return (
    <BrowserRouter>
      <div className="relative w-full min-h-screen bg-modern-grid">
  <div className="z-10 relative text-white p-10">
    <h1 className="text-5xl font-bold">CineChroma</h1>
    <p className="text-gray-400 mt-2">Explore cinema through color.</p>
  </div>
</div>

    </BrowserRouter>
  );
}
