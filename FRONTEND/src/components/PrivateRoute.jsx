// src/components/PrivateRoute.jsx

import { Navigate } from "react-router-dom";

export default function PrivateRoute({ children }) {
    const usuario = JSON.parse(localStorage.getItem("usuario") || "null");
    if (!usuario || !usuario.nombre || !usuario.rol) {
        return <Navigate to="/login" replace />;
    }
    return children;
}