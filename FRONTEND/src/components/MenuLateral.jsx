// src/components/MenuLateral.jsx

import { useNavigate, useLocation } from "react-router-dom";
import "../styles/MenuLateral.css";
import {
    FaHome,
    FaUsers,
    FaFolderOpen,
    FaBuilding,
    FaExchangeAlt
} from "react-icons/fa";

export default function MenuLateral({ rol }) {
    const navigate = useNavigate();
    const location = useLocation();

    //Opciones para admin y mesa de partes
    const opcionesFull = [
        { label: "Inicio", ruta: "/dashboard", icon: <FaHome /> },
        { label: "Áreas", ruta: "/dashboard/areas", icon: <FaBuilding /> },
        { label: "Usuarios", ruta: "/dashboard/usuarios", icon: <FaUsers /> },
        { label: "Trámites Externos", ruta: "/dashboard/tramites-externos", icon: <FaFolderOpen /> },
        { label: "Trámites Internos", ruta: "/dashboard/tramites-internos", icon: <FaExchangeAlt /> },
    ];
    //Opciones para otros roles
    const opcionesLimitadas = [
        { label: "Inicio", ruta: "/dashboard", icon: <FaHome /> },
        { label: "Trámites Externos", ruta: "/dashboard/tramites-externos", icon: <FaFolderOpen /> },
        { label: "Trámites Internos", ruta: "/dashboard/tramites-internos", icon: <FaExchangeAlt /> },
    ];

    const opciones =
        rol === "admin" || rol === "mesa_partes" ? opcionesFull : opcionesLimitadas;

    return (
        <nav className="menu-lateral">
            <ul>
                {opciones.map((op) => (
                    <li
                        key={op.ruta}
                        className={location.pathname === op.ruta ? "activo" : ""}
                        onClick={() => navigate(op.ruta)}
                    >
                        <span className="icono-menu">{op.icon}</span>
                        <span>{op.label}</span>
                    </li>
                ))}
            </ul>
        </nav>
    );
}
