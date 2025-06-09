//src/pages/TramitesExternos.jsx

import { useEffect, useState, useRef } from "react";
import {
    FaSync, FaEye, FaCheck, FaFilePdf, FaCloudUploadAlt, FaReply, FaShare, FaFileExcel, FaShareSquare
} from "react-icons/fa";
import * as XLSX from "xlsx";
import "../styles/TramitesExternos.css";

const ESTADOS = [
    "pendiente",
    "atendido",
    "denegado",
    "derivado",
    "archivado"
];

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

export default function TramitesExternos({ usuarioLogueado }) {
    const [tramites, setTramites] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [tramiteSel, setTramiteSel] = useState(null);
    const [modal, setModal] = useState(false);
    const [modalDerivar, setModalDerivar] = useState(false);
    const [estado, setEstado] = useState("");
    const [respuesta, setRespuesta] = useState("");
    const [pdfRespuesta, setPdfRespuesta] = useState(null);
    const [pdfUrl, setPdfUrl] = useState("");
    const [success, setSuccess] = useState("");
    const [areas, setAreas] = useState([]);
    const [areaDerivar, setAreaDerivar] = useState("");
    const [successDerivar, setSuccessDerivar] = useState("");
    const [errorDerivar, setErrorDerivar] = useState("");
    const fileInputRef = useRef(null);
    const [estadoFiltro, setEstadoFiltro] = useState("");
    const [busqueda, setBusqueda] = useState("");

    const fetchTramites = async () => {
        setLoading(true);
        setError("");
        try {
            if (!usuarioLogueado) {
                setLoading(false);
                return;
            }
            const rol = usuarioLogueado.rol;
            const area_id = usuarioLogueado.area_id;
            const url = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/tramites-externos?rol=${rol}&area_id=${area_id}`;
            const res = await fetch(url);
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Error al cargar trámites");
            setTramites(data.tramites);
        } catch (err) {
            setError(err.message);
        }
        setLoading(false);
    };

    const fetchAreas = async () => {
        try {
            const url = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/areas`;
            const res = await fetch(url);
            const data = await res.json();
            setAreas(data.areas || []);
        } catch {
            setAreas([]);
        }
    };

    useEffect(() => {
        fetchTramites();
        fetchAreas();
    }, []);

    const tramitesFiltrados = tramites
        .filter(t =>
            !estadoFiltro || t.estado === estadoFiltro
        )
        .filter(t => {
            if (!busqueda.trim()) return true;
            const b = busqueda.trim().toLowerCase();
            return (
                t.numero_expediente?.toLowerCase().includes(b) ||
                t.remitente?.toLowerCase().includes(b) ||
                t.asunto?.toLowerCase().includes(b) ||
                t.tipo_documento?.toLowerCase().includes(b) ||
                t.dni_ruc?.toLowerCase().includes(b) ||
                t.email?.toLowerCase().includes(b)
            );
        });

    const exportarExcel = () => {
        const encabezados = [
            "ID", "Nº Expediente", "Remitente", "Asunto", "Tipo Doc.", "Estado", "Fecha Registro",
            "Folios", "Tipo Persona", "DNI/RUC", "Email", "Teléfono"
        ];
        const datos = tramites.map(t => [
            t.id,
            t.numero_expediente,
            t.remitente,
            t.asunto,
            t.tipo_documento,
            t.estado,
            formatearFecha(t.fecha_registro),
            t.folios,
            t.tipo_persona,
            t.dni_ruc,
            t.email,
            t.telefono || "-"
        ]);

        const ws = XLSX.utils.aoa_to_sheet([]);
        const wb = XLSX.utils.book_new();
        const titulo = "REPORTE DE TRÁMITES EXTERNOS";
        XLSX.utils.sheet_add_aoa(ws, [[titulo]], { origin: "A1" });
        ws["!merges"] = [{ s: { r: 0, c: 0 }, e: { r: 0, c: encabezados.length - 1 } }];
        XLSX.utils.sheet_add_aoa(ws, [encabezados], { origin: "A2" });
        XLSX.utils.sheet_add_aoa(ws, datos, { origin: "A3" });
        ws["!cols"] = encabezados.map(() => ({ wch: 18 }));
        XLSX.utils.book_append_sheet(wb, ws, "TramitesExternos");
        XLSX.writeFile(wb, "reporte_tramites_externos.xlsx");
    };

    const abrirDetalle = (t) => {
        setTramiteSel(t);
        setEstado(t.estado);
        setRespuesta("");
        setPdfRespuesta(null);
        setPdfUrl("");
        setModal(true);
        setSuccess("");
        setError("");
    };

    const abrirDerivar = (t) => {
        setTramiteSel(t);
        setAreaDerivar("");
        setModalDerivar(true);
        setSuccessDerivar("");
        setErrorDerivar("");
    };

    const derivarTramite = async (e) => {
        e.preventDefault();
        setErrorDerivar("");
        setSuccessDerivar("");
        if (!tramiteSel || !areaDerivar) {
            setErrorDerivar("Seleccione un área destino.");
            return;
        }
        setLoading(true);
        try {
            const url = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/tramites-externos/${tramiteSel.id}/derivar`;
            const body = { area_id: areaDerivar };
            const res = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body)
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Error al derivar trámite");
            setSuccessDerivar("Trámite derivado exitosamente.");
            setAreaDerivar("");
            fetchTramites();
            setTimeout(() => setModalDerivar(false), 1000);
        } catch (err) {
            setErrorDerivar(err.message);
        }
        setLoading(false);
    };

    const handleEstado = (e) => setEstado(e.target.value);

    const actualizarEstado = async () => {
        if (!tramiteSel) return;
        setLoading(true);
        setError("");
        try {
            const url = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/tramites-externos/${tramiteSel.id}`;
            const res = await fetch(url, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ estado }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Error al actualizar estado");
            setSuccess("Estado actualizado.");
            fetchTramites();
            setTramiteSel({ ...tramiteSel, estado });
        } catch (err) {
            setError(err.message);
        }
        setLoading(false);
    };

    const enviarRespuesta = async (e) => {
        e.preventDefault();
        if (!tramiteSel) return;
        setLoading(true);
        setError("");
        setSuccess("");
        try {
            const formData = new FormData();
            if (respuesta.trim() !== "") formData.append("respuesta", respuesta.trim());
            if (pdfRespuesta) formData.append("pdf_respuesta", pdfRespuesta);
            const url = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/tramites-externos/${tramiteSel.id}/contestar`;
            const res = await fetch(url, {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Error al contestar trámite");
            setSuccess("Respuesta enviada exitosamente.");
            setRespuesta("");
            setPdfRespuesta(null);
            setPdfUrl("");
            fetchTramites();
        } catch (err) {
            setError("Error al enviar respuesta.");
        }
        setLoading(false);
    };

    const verPDF = (ruta) => {
        let url = ruta;
        if (!/^https?:\/\//.test(ruta)) {
            url = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/${ruta}`;
        }
        setPdfUrl(url);
    };

    return (
        <div className="tramites-externos-page">
            <h2>Trámites Externos</h2>
            <div className="toolbar-tramites-ex">
                <button onClick={fetchTramites}><FaSync /> Refrescar</button>
                <button onClick={exportarExcel} style={{ background: "#27ae60", color: "#fff" }}>
                    <FaFileExcel /> Exportar Excel
                </button>
                {/*filtro por estado */}
                <select
                    value={estadoFiltro}
                    onChange={e => setEstadoFiltro(e.target.value)}
                    style={{ marginLeft: 16, padding: "5px 12px" }}
                >
                    <option value="">Todos los estados</option>
                    {ESTADOS.map(est => (
                        <option key={est} value={est}>
                            {est.charAt(0).toUpperCase() + est.slice(1)}
                        </option>
                    ))}
                </select>
                {/* búsqueda texto */}
                <input
                    type="text"
                    placeholder="Buscar trámite..."
                    value={busqueda}
                    onChange={e => setBusqueda(e.target.value)}
                    style={{ marginLeft: 16, padding: "5px 12px", minWidth: 180 }}
                />
            </div>
            {loading ? (
                <div className="loading">Cargando trámites...</div>
            ) : error ? (
                <div className="error">{error}</div>
            ) : (
                <table className="tabla-tramites-externos">
                    <thead>
                        <tr>
                            <th>N°</th>
                            <th>Nº Expediente</th>
                            <th>Remitente</th>
                            <th>Asunto</th>
                            <th>Tipo Doc.</th>
                            <th>Estado</th>
                            <th>Fecha Registro</th>
                            <th>PDF</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tramitesFiltrados.length === 0 ? (
                            <tr>
                                <td colSpan={9}>No hay trámites que mostrar.</td>
                            </tr>
                        ) : (
                            tramitesFiltrados.map((t, idx) => (
                                <tr key={t.id}>
                                    <td>{idx + 1}</td>
                                    <td>{t.numero_expediente}</td>
                                    <td>{t.remitente}</td>
                                    <td>{t.asunto}</td>
                                    <td>{t.tipo_documento}</td>
                                    <td>
                                        <span className={"estado " + t.estado}>{t.estado}</span>
                                    </td>
                                    <td>{formatearFecha(t.fecha_registro)}</td>
                                    <td>
                                        {t.archivo ? (
                                            <button
                                                className="btn-accion"
                                                title="Ver PDF"
                                                onClick={() => verPDF(t.archivo)}
                                                type="button"
                                            >
                                                <FaFilePdf />
                                            </button>
                                        ) : <span style={{ fontSize: 13, color: "#888" }}>-</span>}
                                    </td>
                                    <td style={{ display: "flex", gap: 6 }}>
                                        <button
                                            className="btn-accion"
                                            onClick={() => abrirDetalle(t)}
                                            title="Ver Detalles y Atender"
                                        >
                                            <FaEye />
                                        </button>
                                        <button
                                            className="btn-accion"
                                            style={{ background: "#ffa726", color: "#1a237e" }}
                                            onClick={() => abrirDerivar(t)}
                                            title="Derivar Trámite"
                                        >
                                            <FaShareSquare />
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            )}

            {/* MODAL PDF */}
            {pdfUrl && (
                <div className="modal-bg-pdf" onClick={() => setPdfUrl("")}>
                    <div className="modal-pdf-viewer" style={{ maxWidth: "1100px", width: "92vw", minHeight: "70vh", height: "auto" }} onClick={e => e.stopPropagation()}>
                        <iframe
                            src={pdfUrl}
                            title="PDF"
                            width="100%"
                            height="650px"
                            style={{ border: 0, display: "block", borderRadius: "14px 14px 0 0" }}
                        />
                        <button className="btn-modal cerrar" onClick={() => setPdfUrl("")}>Cerrar PDF</button>
                    </div>
                </div>
            )}

            {/* MODAL DETALLE Y ATENDER */}
            {modal && tramiteSel && (
                <div className="municipal-modal-bg" onClick={() => setModal(false)}>
                    <div className="municipal-modal-box" onClick={e => e.stopPropagation()}>
                        <button className="municipal-modal-close" onClick={() => setModal(false)}>
                            &times;
                        </button>

                        <div className="municipal-modal-header">
                            <div className="municipal-modal-titles">
                                <h2>
                                    <span role="img" aria-label="folder">📁</span> Detalle de Trámite
                                </h2>
                                <span className="municipal-modal-subtitle">
                                    Expediente&nbsp;<b>{tramiteSel.numero_expediente}</b>
                                </span>
                            </div>
                            <div className={`municipal-estado-label estado-${estado}`}>
                                {estado.charAt(0).toUpperCase() + estado.slice(1)}
                            </div>
                        </div>

                        <div className="municipal-modal-content">
                            <div className="municipal-tramite-grid">
                                <div><span>ID:</span> {tramiteSel.id}</div>
                                <div><span>Fecha y Hora:</span> {formatearFecha(tramiteSel.fecha_registro)}</div>
                                <div><span>Remitente:</span> {tramiteSel.remitente}</div>
                                <div><span>Asunto:</span> {tramiteSel.asunto}</div>
                                <div><span>Código Seguridad:</span> {tramiteSel.codigo_seguridad}</div>
                                <div><span>Folios:</span> {tramiteSel.folios}</div>
                                <div><span>Tipo Persona:</span> {tramiteSel.tipo_persona}</div>
                                <div><span>DNI/RUC:</span> {tramiteSel.dni_ruc}</div>
                                <div><span>Email:</span> {tramiteSel.email}</div>
                                <div><span>Teléfono:</span> {tramiteSel.telefono || "-"}</div>
                            </div>

                            <div className="municipal-estado-box">
                                <label>
                                    <b>Estado:</b>
                                    <select value={estado} onChange={handleEstado} className="municipal-select">
                                        {ESTADOS.map(est => (
                                            <option key={est} value={est}>
                                                {est.charAt(0).toUpperCase() + est.slice(1)}
                                            </option>
                                        ))}
                                    </select>
                                </label>
                                <button className="municipal-btn municipal-btn-estado" onClick={actualizarEstado} disabled={loading}>
                                    <FaCheck /> Guardar Estado
                                </button>
                            </div>

                            <form className="municipal-form-horizontal" onSubmit={enviarRespuesta}>
                                <label>
                                    <b>Contestar trámite:</b>
                                    <textarea
                                        value={respuesta}
                                        onChange={e => setRespuesta(e.target.value)}
                                        placeholder="Escribe tu respuesta aquí..."
                                        rows={4}
                                        className="municipal-textarea"
                                    />
                                </label>
                                <div className="municipal-form-adjuntar">
                                    <label htmlFor="pdfRespuesta" className="municipal-btn municipal-btn-adjuntar">
                                        <FaCloudUploadAlt /> Adjuntar PDF respuesta
                                    </label>
                                    <input
                                        id="pdfRespuesta"
                                        type="file"
                                        accept="application/pdf"
                                        style={{ display: "none" }}
                                        ref={fileInputRef}
                                        onChange={e => setPdfRespuesta(e.target.files[0])}
                                    />
                                    {pdfRespuesta && (
                                        <span className="municipal-adjunto-file">
                                            <FaFilePdf style={{ color: "#d32f2f" }} />
                                            {pdfRespuesta.name}
                                            <button
                                                type="button"
                                                className="municipal-btn-cancelar-adjunto"
                                                onClick={() => { setPdfRespuesta(null); fileInputRef.current.value = ""; }}
                                            >x</button>
                                        </span>
                                    )}
                                </div>
                                <div className="municipal-form-actions">
                                    <button
                                        className="municipal-btn municipal-btn-primary"
                                        type="submit"
                                        disabled={loading || (!respuesta.trim() && !pdfRespuesta)}
                                    >
                                        <FaReply /> Enviar Contestación
                                    </button>
                                    <button
                                        className="municipal-btn municipal-btn-secondary"
                                        type="button"
                                        onClick={() => setModal(false)}
                                    >
                                        Cerrar
                                    </button>
                                </div>
                                {success && <span className="municipal-success">{success}</span>}
                                {error && <span className="municipal-error">{error}</span>}
                            </form>
                        </div>
                    </div>
                </div>
            )}

            {/* MODAL DERIVAR */}
            {modalDerivar && tramiteSel && (
                <div className="municipal-modal-bg" onClick={() => setModalDerivar(false)}>
                    <div className="municipal-modal-box" onClick={e => e.stopPropagation()}>
                        <button className="municipal-modal-close" onClick={() => setModalDerivar(false)}>
                            &times;
                        </button>
                        <div className="municipal-modal-header">
                            <div className="municipal-modal-titles">
                                <h2>
                                    <span role="img" aria-label="arrow">➡️</span> Derivar Trámite
                                </h2>
                                <span className="municipal-modal-subtitle">
                                    Expediente&nbsp;<b>{tramiteSel.numero_expediente}</b>
                                </span>
                            </div>
                        </div>
                        <div className="municipal-modal-content">
                            <form className="municipal-form-horizontal" onSubmit={derivarTramite}>
                                <label>
                                    <b>Área destino:</b>
                                    <select
                                        value={areaDerivar}
                                        onChange={e => setAreaDerivar(e.target.value)}
                                        required
                                        className="municipal-select"
                                    >
                                        <option value="">Seleccione área</option>
                                        {areas.map(a => (
                                            <option value={a.id} key={a.id}>{a.nombre}</option>
                                        ))}
                                    </select>
                                </label>
                                <div className="municipal-form-actions">
                                    <button
                                        className="municipal-btn municipal-btn-warning"
                                        type="submit"
                                        disabled={loading || !areaDerivar}
                                    >
                                        <FaShareSquare /> Derivar
                                    </button>
                                    <button
                                        className="municipal-btn municipal-btn-secondary"
                                        type="button"
                                        onClick={() => setModalDerivar(false)}
                                    >
                                        Cancelar
                                    </button>
                                </div>
                                {successDerivar && <span className="municipal-success">{successDerivar}</span>}
                                {errorDerivar && <span className="municipal-error">{errorDerivar}</span>}
                            </form>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
