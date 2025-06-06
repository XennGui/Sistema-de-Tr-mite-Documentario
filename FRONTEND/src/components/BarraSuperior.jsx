// src/components/BarraSuperior.jsx

import { useNavigate, useLocation } from "react-router-dom";
import "../styles/BarraSuperior.css";

export default function BarraSuperior({ mostrarBoton = true }) {
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <nav className="barra-superior">
            <div className="contenido-barra">
                <span
                    className="titulo-barra"
                    style={{ cursor: "pointer" }}
                    onClick={() => navigate("/")}
                >
                    Municipalidad de Yau
                </span>
                {mostrarBoton && location.pathname !== "/login" && (
                    <button
                        className="boton-login-barra"
                        onClick={() => navigate("/login")}
                    >
                        Iniciar sesión
                    </button>
                )}
            </div>
        </nav>
    );
}