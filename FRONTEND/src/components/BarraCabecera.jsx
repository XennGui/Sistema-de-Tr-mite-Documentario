// src/components/BarraCabecera.jsx

import "../styles/BarraCabecera.css";
import { FaUserCircle, FaBuilding, FaChevronDown, FaSignOutAlt } from "react-icons/fa";
import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";


export default function BarraCabecera() {
    const [usuario, setUsuario] = useState(() =>
        JSON.parse(localStorage.getItem("usuario") || "{}")
    );

    const [menuAbierto, setMenuAbierto] = useState(false);
    const menuRef = useRef();
    const navigate = useNavigate();

    // Actualiza el usuario cada vez que se abre el menú (por si cambió el nombre)
    useEffect(() => {
        if (menuAbierto) {
            const usuarioActualizado = JSON.parse(localStorage.getItem("usuario") || "{}");
            setUsuario(usuarioActualizado);
        }
    }, [menuAbierto]);

    // Escucha cambios en localStorage desde otras pestañas/ventanas
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

    // Cierra el menú si se hace clic fuera de él
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

    return (
        <header className="cabecera-principal">
            <div className="cabecera-titulo">
                <FaBuilding style={{ marginRight: "12px", fontSize: "2rem" }} />
                Municipalidad de Yau
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
                            {usuario.rol ? usuario.rol.replace("_", " ") : ""}
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