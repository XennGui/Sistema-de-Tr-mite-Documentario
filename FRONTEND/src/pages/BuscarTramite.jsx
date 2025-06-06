// src/pages/BuscarTramite.jsx

import { useState } from "react";
import { FaSearch, FaFileAlt, FaUser, FaEnvelope, FaPhone, FaIdCard, FaListAlt, FaFilePdf, FaClock } from "react-icons/fa";
import BarraSuperior from "../components/BarraSuperior";
import "../styles/BuscarTramite.css";

export default function BuscarTramite() {
    const [expediente, setExpediente] = useState("");
    const [codigo, setCodigo] = useState("");
    const [error, setError] = useState("");
    const [tramite, setTramite] = useState(null);
    const [seguimiento, setSeguimiento] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleBuscar = async (e) => {
        e.preventDefault();
        setError("");
        setTramite(null);
        setSeguimiento([]);
        if (!expediente.trim() || !codigo.trim()) {
            setError("Ingrese el número de expediente y el código de seguridad.");
            return;
        }
        setLoading(true);
        try {
            // 1. Buscar trámite
            const url = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/tramites-externos/buscar?numero_expediente=${encodeURIComponent(expediente)}&codigo_seguridad=${encodeURIComponent(codigo)}`;
            const res = await fetch(url);
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "No se encontró el trámite.");
            setTramite(data.tramite);

            // 2. Buscar seguimiento del trámite
            const urlSeg = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/tramites-externos/${data.tramite.id}/seguimiento`;
            const resSeg = await fetch(urlSeg);
            const dataSeg = await resSeg.json();
            setSeguimiento(dataSeg.seguimiento || []);
        } catch (err) {
            setError(err.message);
        }
        setLoading(false);
    };

    return (
        <div>
            <BarraSuperior mostrarBoton={true} />
            <div className="buscar-tramite-contenedor">
                <div className="buscar-tramite-form-card">
                    <h2><FaSearch className="buscar-tramite-icon" /> Buscar Trámite</h2>
                    <form className="buscar-tramite-form" onSubmit={handleBuscar}>
                        <div>
                            <label>Nº de expediente:</label>
                            <input
                                value={expediente}
                                onChange={e => setExpediente(e.target.value)}
                                required
                                maxLength={50}
                            />
                        </div>
                        <div>
                            <label>Código de seguridad:</label>
                            <input
                                value={codigo}
                                onChange={e => setCodigo(e.target.value)}
                                required
                                maxLength={20}
                            />
                        </div>
                        <button type="submit" className="buscar-tramite-btn" disabled={loading}>
                            <FaSearch style={{ marginRight: 6 }} />
                            Buscar
                        </button>
                        {error && <div className="buscar-tramite-error">{error}</div>}
                    </form>
                </div>

                {tramite && (
                    <div className="tramite-info-card">
                        <h2>
                            <FaFileAlt className="tramite-info-icon" />
                            Información del Trámite
                        </h2>
                        <div className="tramite-info-formulario">
                            <div>
                                <label><FaClock className="ti-icon" /> Fecha y Hora:</label>
                                <div>{new Date(tramite.fecha_registro).toLocaleString()}</div>
                            </div>
                            <div>
                                <label><FaUser className="ti-icon" /> Remitente:</label>
                                <div>{tramite.remitente}</div>
                            </div>
                            <div>
                                <label><FaFileAlt className="ti-icon" /> Tipo documento:</label>
                                <div>{tramite.tipo_documento}</div>
                            </div>
                            <div>
                                <label><FaFileAlt className="ti-icon" /> Folios:</label>
                                <div>{tramite.folios}</div>
                            </div>
                            <div>
                                <label><FaFileAlt className="ti-icon" /> Asunto:</label>
                                <div>{tramite.asunto}</div>
                            </div>
                            <div>
                                <label><FaIdCard className="ti-icon" /> DNI/RUC:</label>
                                <div>{tramite.dni_ruc}</div>
                            </div>
                            <div>
                                <label><FaEnvelope className="ti-icon" /> Correo:</label>
                                <div>{tramite.email}</div>
                            </div>
                            <div>
                                <label><FaPhone className="ti-icon" /> Teléfono:</label>
                                <div>{tramite.telefono || "-"}</div>
                            </div>
                            <div>
                                <label><FaFileAlt className="ti-icon" /> Nº de expediente:</label>
                                <div>{tramite.numero_expediente}</div>
                            </div>
                            <div>
                                <label><FaListAlt className="ti-icon" /> Estado:</label>
                                <div>{tramite.estado}</div>
                            </div>
                        </div>
                    </div>
                )}

                {tramite && (
                    <div className="seguimiento-card">
                        <h2>
                            <FaListAlt className="seguimiento-icon" />
                            SEGUIMIENTO DE TRÁMITE
                        </h2>
                        <div className="seguimiento-table-wrapper">
                            <table className="seguimiento-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Fecha/Hora</th>
                                        <th>Acción</th>
                                        <th>Descripción</th>
                                        <th>Adjunto</th>
                                        <th>Usuario</th>
                                        <th>Área</th>
                                        <th>Observaciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {seguimiento.length > 0 ? seguimiento.map((mov, i) => (
                                        <tr key={mov.id || i}>
                                            <td>{mov.id}</td>
                                            <td>{new Date(mov.fecha_hora).toLocaleString()}</td>
                                            <td>{mov.accion}</td>
                                            <td>{mov.descripcion}</td>
                                            <td>
                                                {mov.adjunto ? (
                                                    <a href={mov.adjunto} target="_blank" rel="noopener noreferrer">
                                                        <FaFilePdf /> Ver
                                                    </a>
                                                ) : "-"}
                                            </td>
                                            <td>{mov.usuario || "-"}</td>
                                            <td>{mov.area || "-"}</td>
                                            <td>{mov.observaciones || "-"}</td>
                                        </tr>
                                    )) : (
                                        <tr>
                                            <td colSpan={8} style={{ textAlign: "center", color: "#888" }}>No hay movimientos registrados.</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
