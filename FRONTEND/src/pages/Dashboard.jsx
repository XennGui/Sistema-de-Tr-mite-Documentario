// src/pages/Dashboard.jsx
import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import BarraCabecera from "../components/BarraCabecera";
import MenuLateral from "../components/MenuLateral";
import DashboardInicio from "./DashboardInicio";
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

    // Muestra DashboardInicio solo en /dashboard (no subrutas)
    const isInicio = location.pathname === "/dashboard";

    return (
        <div className="dashboard-contenedor">
            <BarraCabecera usuario={usuario} />
            <div className="dashboard-main">
                <MenuLateral rol={usuario.rol} />
                <div className="dashboard-contenido">
                    {isInicio && <DashboardInicio usuario={usuario} />}
                    {/* Aquí puedes renderizar las otras rutas */}
                </div>
            </div>
        </div>
    );
}