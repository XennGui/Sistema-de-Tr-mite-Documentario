// src/pages/Login.jsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import BarraSuperior from "../components/BarraSuperior";
import { loginUsuario } from "../services/usuarioService";
import "../styles/Login.css";
import { FaUserCircle, FaEnvelope, FaLock, FaEye, FaEyeSlash } from "react-icons/fa";

export default function Login() {
    const [identificador, setIdentificador] = useState("");
    const [password, setPassword] = useState("");
    const [verPassword, setVerPassword] = useState(false);
    const [error, setError] = useState("");
    const [cargando, setCargando] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setCargando(true);
        const respuesta = await loginUsuario(identificador, password);
        setCargando(false);
        if (respuesta.exito) {
            localStorage.setItem("usuario", JSON.stringify(respuesta.usuario));
            navigate("/dashboard", { replace: true });
        } else {
            setError(respuesta.mensaje || "Usuario o contraseña incorrectos.");
        }
    };


    return (
        <div className="login-bg">
            <BarraSuperior mostrarBoton={false} />
            <div className="login-container">
                <div className="login-header">
                    <FaUserCircle className="login-icon" />
                    <h2>INICIAR SESIÓN</h2>
                    <p className="login-subtitle">Sistema Municipal</p>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="login-field">
                        <label>Correo o usuario</label>
                        <div className="icon-input-group">
                            <span className="icon-input">
                                {identificador.includes("@") ? <FaEnvelope /> : <FaUserCircle />}
                            </span>
                            <input
                                type="text"
                                value={identificador}
                                onChange={e => setIdentificador(e.target.value)}
                                autoFocus
                                required
                                placeholder="Ingrese su correo o usuario"
                            />
                        </div>
                    </div>
                    <div className="login-field">
                        <label>Contraseña</label>
                        <div className="icon-input-group">
                            <span className="icon-input"><FaLock /></span>
                            <input
                                type={verPassword ? "text" : "password"}
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                required
                                placeholder="Ingrese su contraseña"
                            />
                            <span
                                className="icon-eye"
                                onClick={() => setVerPassword((v) => !v)}
                                tabIndex={0}
                                aria-label={verPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                                title={verPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                            >
                                {verPassword ? <FaEye /> : <FaEyeSlash />}
                            </span>
                        </div>
                    </div>
                    {error && <div className="login-error">{error}</div>}
                    <div className="login-buttons">
                        <button
                            type="button"
                            className="login-secondary"
                            onClick={() => navigate("/")}
                            disabled={cargando}
                        >
                            Atrás
                        </button>
                        <button type="submit" className="login-primary" disabled={cargando}>
                            {cargando ? "Ingresando..." : "Ingresar"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}