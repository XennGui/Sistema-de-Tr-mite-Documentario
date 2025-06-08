// src/components/BarraCabecera.jsx

import "../styles/BarraCabecera.css";
import { FaUserCircle, FaBuilding, FaChevronDown, FaSignOutAlt } from "react-icons/fa";
import { useState, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import ChatbotMunicipal from "./ChatbotMunicipal";

const ROLES_OPTIONS = [
    { value: "admin", label: "Administrador" },
    { value: "mesa_partes", label: "Mesa de partes" },
    { value: "usuario", label: "Jefe" },
    { value: "auxiliar", label: "Auxiliar" },
];

export default function BarraCabecera() {
    const [usuario, setUsuario] = useState(() =>
        JSON.parse(localStorage.getItem("usuario") || "{}")
    );
    const [menuAbierto, setMenuAbierto] = useState(false);
    const menuRef = useRef();
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        if (!usuario || !usuario.nombre || !usuario.rol) {
            navigate("/login", { replace: true });
        }
    }, [usuario, navigate]);

    if (location.pathname === "/login") return null;

    useEffect(() => {
        if (menuAbierto) {
            const usuarioActualizado = JSON.parse(localStorage.getItem("usuario") || "{}");
            setUsuario(usuarioActualizado);
        }
    }, [menuAbierto]);

    useEffect(() => {
        function handleStorageChange(e) {
            if (e.key === "usuario") {
                const usuarioActualizado = JSON.parse(e.newValue || "{}");
                setUsuario(usuarioActualizado);
            }
        }
        window.addEventListener("storage", handleStorageChange);
        return () => window.removeEventListener("storage", handleStorageChange);
    }, []);

    useEffect(() => {
        function handleClickOutside(e) {
            if (menuRef.current && !menuRef.current.contains(e.target)) {
                setMenuAbierto(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const cerrarSesion = () => {
        localStorage.removeItem("usuario");
        setMenuAbierto(false);
        navigate("/login", { replace: true });
    };

    const rolLegible = usuario.rol
        ? (ROLES_OPTIONS.find(r => r.value === usuario.rol)?.label || usuario.rol)
        : "";

    return (
        <header className="cabecera-principal">
            <div className="cabecera-titulo">
                <FaBuilding style={{ marginRight: "12px", fontSize: "2rem" }} />
                Municipalidad de Yau
            </div>
            {/* CHATBOT EN EL CENTRO DE LA CABECERA */}
            <div className="cabecera-chatbot-central">
                <ChatbotMunicipal />
            </div>
            <div className="cabecera-usuario" ref={menuRef}>
                <button
                    className="cabecera-usuario-btn"
                    onClick={() => setMenuAbierto(v => !v)}
                    title="Opciones de usuario"
                >
                    <FaUserCircle style={{ fontSize: "1.7rem", marginRight: "8px" }} />
                    <div className="cabecera-nombre-rol">
                        <div>{usuario.nombre || "Usuario"}</div>
                        <div className="cabecera-rol">
                            {rolLegible}
                        </div>
                    </div>
                    <FaChevronDown style={{ marginLeft: 8 }} />
                </button>
                {menuAbierto && (
                    <div className="cabecera-menu">
                        <button className="cabecera-cerrar-sesion" onClick={cerrarSesion}>
                            <FaSignOutAlt style={{ marginRight: 7 }} />
                            Cerrar sesión
                        </button>
                    </div>
                )}
            </div>
        </header>
    );
}