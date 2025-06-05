// src/pages/Dashboard.jsx
import { useEffect, useState } from "react";
import { useNavigate, useLocation, Routes, Route } from "react-router-dom";
import BarraCabecera from "../components/BarraCabecera";
import MenuLateral from "../components/MenuLateral";
import DashboardInicio from "./DashboardInicio";
import Areas from "./Areas";
import Usuarios from "./Usuarios";
import "../styles/Dashboard.css";

export default function Dashboard() {
    const [usuario, setUsuario] = useState(null);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const usuarioGuardado = localStorage.getItem("usuario");
        if (!usuarioGuardado) {
            navigate("/login", { replace: true });
        } else {
            setUsuario(JSON.parse(usuarioGuardado));
        }
    }, [navigate]);

    if (!usuario) return null;

    return (
        <div className="dashboard-contenedor">
            <BarraCabecera usuario={usuario} />
            <div className="dashboard-main">
                <MenuLateral rol={usuario.rol} />
                <div className="dashboard-contenido">
                    <Routes>
                        <Route path="/" element={<DashboardInicio usuario={usuario} />} />
                        <Route path="areas" element={<Areas />} />
                        <Route path="usuarios" element={<Usuarios />} />
                    </Routes>
                </div>
            </div>
        </div>
    );
}