// src/App.jsx

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import PrivateRoute from "./components/PrivateRoute";
import RegistrarTramite from "./pages/RegistrarTramite"; 
import BuscarTramite from "./pages/BuscarTramite";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        {/* Ruta pública para el registro de trámite externo */}
        <Route path="/registrar-tramite" element={<RegistrarTramite />} />
        <Route path="/buscar-tramite" element={<BuscarTramite />} />
        {/* Rutas privadas */}
        <Route
          path="/dashboard/*"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        {/* Redirecciona cualquier otra ruta a Home */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}