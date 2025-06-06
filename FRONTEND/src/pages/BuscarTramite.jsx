// RUTA: src/pages/BuscarTramite.jsx
import { useState } from "react";
import { FaSearch, FaFileAlt, FaUser, FaEnvelope, FaPhone, FaIdCard, FaListAlt, FaFilePdf, FaClock } from "react-icons/fa";
import BarraSuperior from "../components/BarraSuperior";
import "../styles/BuscarTramite.css";

function formatearFecha(fechaIso) {
    if (!fechaIso) return "-";
    try {
        const fecha = new Date(fechaIso);
        return fecha.toLocaleString("es-PE", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });
    } catch {
        return fechaIso;
    }
}

export default function BuscarTramite() {
    const [expediente, setExpediente] = useState("");
    const [codigo, setCodigo] = useState("");
    const [error, setError] = useState("");
    const [tramite, setTramite] = useState(null);
    const [seguimiento, setSeguimiento] = useState([]);
    const [loading, setLoading] = useState(false);
    const [pdfUrl, setPdfUrl] = useState(""); // Visor PDF

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
            // Buscar trámite
            const url = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/tramites-externos/buscar?numero_expediente=${encodeURIComponent(expediente)}&codigo_seguridad=${encodeURIComponent(codigo)}`;
            const res = await fetch(url);
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "No se encontró el trámite.");
            setTramite(data.tramite);

            // Buscar seguimiento del trámite
            const urlSeg = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/tramites-externos/${data.tramite.id}/seguimiento`;
            const resSeg = await fetch(urlSeg);
            const dataSeg = await resSeg.json();
            setSeguimiento(dataSeg.seguimiento || []);
        } catch (err) {
            setError(err.message);
        }
        setLoading(false);
    };

    const abrirPDF = (ruta) => {
        let url = ruta;
        if (!/^https?:\/\//.test(ruta)) {
            url = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/${ruta}`;
        }
        setPdfUrl(url);
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
                                <div>{formatearFecha(tramite.fecha_registro)}</div>
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
                            <div style={{ marginTop: 16 }}>
                                <label><FaFilePdf className="ti-icon" /> Documento PDF enviado:</label>
                                {tramite.archivo ? (
                                    <button
                                        className="btn-verpdf"
                                        onClick={() => abrirPDF(tramite.archivo)}
                                        type="button"
                                    >
                                        <FaFilePdf /> Ver PDF
                                    </button>
                                ) : <span style={{ color: "#888" }}>No disponible</span>}
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
                                        <th>Fecha/Hora</th>
                                        <th>Acción</th>
                                        <th>Descripción</th>
                                        <th>Área</th>
                                        <th>Observaciones</th>
                                        <th>Adjunto PDF</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {seguimiento.length > 0 ? seguimiento.map((mov, i) => (
                                        <tr key={mov.id || i}>
                                            <td>{formatearFecha(mov.fecha_hora)}</td>
                                            <td>{mov.accion}</td>
                                            <td>{mov.descripcion}</td>
                                            <td>{mov.area || "-"}</td>
                                            <td>{mov.observaciones || "Ninguno"}</td>
                                            <td>
                                                {mov.adjunto ? (
                                                    <button
                                                        className="btn-verpdf"
                                                        onClick={() => abrirPDF(mov.adjunto)}
                                                        type="button"
                                                        style={{ color: "#d32f2f", fontSize: 16 }}
                                                    >
                                                        <FaFilePdf /> Ver
                                                    </button>
                                                ) : "-"}
                                            </td>
                                        </tr>
                                    )) : (
                                        <tr>
                                            <td colSpan={6} style={{ textAlign: "center", color: "#888" }}>No hay movimientos registrados.</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* MODAL VISOR PDF GRANDE */}
                {pdfUrl && (
                    <div
                        style={{
                            position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh",
                            background: "rgba(30,40,60,0.22)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000
                        }}
                        onClick={() => setPdfUrl("")}
                    >
                        <div
                            style={{
                                background: "#fff", borderRadius: 14, boxShadow: "0 4px 40px rgba(0,0,0,0.23)",
                                width: "92vw", maxWidth: 1100, minHeight: "70vh", padding: 0, position: "relative"
                            }}
                            onClick={e => e.stopPropagation()}
                        >
                            <iframe
                                src={pdfUrl}
                                title="PDF"
                                width="100%"
                                height="700px"
                                style={{ border: 0, display: "block", borderRadius: "14px 14px 0 0" }}
                            />
                            <button
                                style={{
                                    display: "block",
                                    margin: "12px auto 25px auto",
                                    padding: "10px 36px",
                                    border: "none",
                                    borderRadius: 6,
                                    background: "#2d7ff9",
                                    color: "white",
                                    fontSize: 18,
                                    cursor: "pointer"
                                }}
                                onClick={() => setPdfUrl("")}
                            >
                                Cerrar PDF
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
