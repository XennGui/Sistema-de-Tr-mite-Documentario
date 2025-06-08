// src/components/BarraSuperior.jsx

import { useNavigate, useLocation } from "react-router-dom";
import { FaUser, FaBuilding } from "react-icons/fa";
import "../styles/BarraSuperior.css";

export default function BarraSuperior({ mostrarBoton = true }) {
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <nav className="barra-superior">
            <div className="contenido-barra">
                <div className="logo-titulo" onClick={() => navigate("/")}>
                    <FaBuilding className="icono-municipio" />
                    <span className="titulo-barra">
                        Municipalidad de <span className="titulo-destacado">Yau</span>
                    </span>
                </div>
                {mostrarBoton && location.pathname !== "/login" && (
                    <button
                        className="boton-login-barra"
                        onClick={() => navigate("/login")}
                    >
                        <FaUser className="icono-usuario" />
                        Iniciar sesión
                    </button>
                )}
            </div>
        </nav>
    );
}