// src/pages/TramitesInternos.jsx

import { useEffect, useState, useRef } from "react";
import { FaSync, FaEye, FaCheck, FaReply, FaShareSquare, FaFilePdf, FaCloudUploadAlt, FaPlusCircle } from "react-icons/fa";
import "../styles/TramitesInternos.css";

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

export default function TramitesInternos({ usuarioLogueado }) {
    const [tramites, setTramites] = useState([]);
    const [areas, setAreas] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [formVisible, setFormVisible] = useState(false);
    const [form, setForm] = useState({
        numero_referencia: "",
        asunto: "",
        contenido: "",
        folios: 1,
        archivo: null,
        remitente_id: usuarioLogueado?.id || 0,
        area_origen_id: usuarioLogueado?.area_id || 0,
        area_destino_id: "",
        prioridad: 3,
    });
    const [tramiteSel, setTramiteSel] = useState(null);
    const [modal, setModal] = useState(false);
    const [modalDerivar, setModalDerivar] = useState(false);
    const [modalContestar, setModalContestar] = useState(false);
    const [modalPDF, setModalPDF] = useState({ mostrar: false, url: "" });
    const [seguimiento, setSeguimiento] = useState([]);
    const [respuesta, setRespuesta] = useState("");
    const [pdfRespuesta, setPdfRespuesta] = useState(null);
    const [areaDerivar, setAreaDerivar] = useState("");
    const [successMsg, setSuccessMsg] = useState("");
    const [errorMsg, setErrorMsg] = useState("");
    const [estadoFiltro, setEstadoFiltro] = useState(""); 
    const [busqueda, setBusqueda] = useState(""); 
    const fileInputRef = useRef(null);
    const fileInputFormRef = useRef(null);
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

    //cargar trámites y áreas
    useEffect(() => {
        fetchTramites();
        fetchAreas();
    }, []);

    const fetchTramites = async () => {
        setLoading(true);
        setError("");
        try {
            const rol = usuarioLogueado.rol;
            const area_id = usuarioLogueado.area_id;
            const url = `${apiUrl}/tramites-internos?rol=${rol}&area_id=${area_id}`;
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
            const url = `${apiUrl}/areas`;
            const res = await fetch(url);
            const data = await res.json();
            setAreas(data.areas || []);
        } catch {
            setAreas([]);
        }
    };

    const fetchSeguimiento = async (id) => {
        try {
            const url = `${apiUrl}/tramites-internos/${id}/seguimiento`;
            const res = await fetch(url);
            const data = await res.json();
            setSeguimiento(data.seguimiento || []);
        } catch {
            setSeguimiento([]);
        }
    };

    //crear trámite interno
    const handleFormChange = e => {
        const { name, value, files } = e.target;
        if (name === "archivo") {
            setForm({ ...form, archivo: files[0] });
        } else {
            setForm({ ...form, [name]: value });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        setSuccess("");
        try {
            const formData = new FormData();
            Object.entries(form).forEach(([key, val]) => {
                if (val !== null && val !== undefined) formData.append(key, val);
            });
            const url = `${apiUrl}/tramites-internos/`;
            const res = await fetch(url, { method: "POST", body: formData });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Error al crear trámite interno");
            setSuccess("Trámite creado correctamente.");
            setTimeout(() => setSuccess(""), 1800);
            setFormVisible(false);
            setForm({
                numero_referencia: "",
                asunto: "",
                contenido: "",
                folios: 1,
                archivo: null,
                remitente_id: usuarioLogueado?.id || 0,
                area_origen_id: usuarioLogueado?.area_id || 0,
                area_destino_id: "",
                prioridad: 3,
            });
            if (fileInputFormRef.current) fileInputFormRef.current.value = "";
            fetchTramites();
        } catch (err) {
            setError(err.message || "Error al crear trámite interno");
            setTimeout(() => setError(""), 2000);
        }
        setLoading(false);
    };

    const abrirDetalle = (t) => {
        setTramiteSel(t);
        setModal(true);
        fetchSeguimiento(t.id);
    };

    const abrirDerivar = (t) => {
        setTramiteSel(t);
        setAreaDerivar("");
        setModalDerivar(true);
    };

    const abrirContestar = (t) => {
        setTramiteSel(t);
        setRespuesta("");
        setPdfRespuesta(null);
        setModalContestar(true);
    };

    const derivarTramite = async (e) => {
        e.preventDefault();
        setErrorMsg("");
        setSuccessMsg("");
        if (!tramiteSel || !areaDerivar) {
            setErrorMsg("Seleccione un área destino.");
            return;
        }
        setLoading(true);
        try {
            const url = `${apiUrl}/tramites-internos/${tramiteSel.id}/derivar`;
            const body = { area_id: areaDerivar, usuario_id: usuarioLogueado.id };
            const res = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Error al derivar trámite");
            setSuccessMsg("Trámite derivado exitosamente.");
            setTimeout(() => setSuccessMsg(""), 1500);
            setTimeout(() => setModalDerivar(false), 900);
            setAreaDerivar("");
            fetchTramites();
        } catch (err) {
            setErrorMsg(err.message);
            setTimeout(() => setErrorMsg(""), 2500);
        }
        setLoading(false);
    };

    // recibe trámite (solo si el trámite está en estado derivado y el usuario es del área destino)
    const recibirTramite = async (t) => {
        setTramiteSel(t);
        setLoading(true);
        setErrorMsg("");
        try {
            const url = `${apiUrl}/tramites-internos/${t.id}/recibir`;
            const res = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ usuario_id: usuarioLogueado.id }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Error al recibir trámite");
            setSuccessMsg("Trámite recibido correctamente.");
            setTimeout(() => setSuccessMsg(""), 1500);
            fetchTramites();
            if (tramiteSel && tramiteSel.id === t.id) fetchSeguimiento(t.id);
        } catch (err) {
            setErrorMsg(err.message);
            setTimeout(() => setErrorMsg(""), 2500);
        }
        setLoading(false);
    };

    const contestarTramite = async (e) => {
        e.preventDefault();
        setLoading(true);
        setErrorMsg("");
        setSuccessMsg("");
        try {
            const formData = new FormData();
            formData.append("usuario_id", usuarioLogueado.id);
            if (respuesta.trim() !== "") formData.append("respuesta", respuesta.trim());
            if (pdfRespuesta) formData.append("pdf_respuesta", pdfRespuesta);
            const url = `${apiUrl}/tramites-internos/${tramiteSel.id}/contestar`;
            const res = await fetch(url, { method: "POST", body: formData });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Error al contestar trámite");
            setSuccessMsg("Respuesta enviada exitosamente.");
            setTimeout(() => setSuccessMsg(""), 1500);
            setRespuesta("");
            setPdfRespuesta(null);
            fetchTramites();
            fetchSeguimiento(tramiteSel.id);
            setTimeout(() => setModalContestar(false), 900);
        } catch (err) {
            setErrorMsg("Error al enviar respuesta.");
            setTimeout(() => setErrorMsg(""), 2500);
        }
        setLoading(false);
    };

    const verPDF = (ruta) => {
        if (!ruta) return;
        let url = ruta;
        if (!/^https?:\/\//.test(ruta)) {
            const parts = ruta.split(/[\\/]/);
            const carpeta = parts[0];
            const nombre_archivo = parts.slice(1).join("/");
            url = `${apiUrl}/tramites-internos/archivo/${carpeta}/${nombre_archivo}`;
        }
        setModalPDF({ mostrar: true, url });
    };

    const nombreArea = (area_id) => {
        const area = areas.find(a => a.id === area_id);
        return area ? area.nombre : area_id;
    };

    const puedeRecibir = (t) =>
        t.estado === "derivado" && usuarioLogueado.area_id === t.area_destino_id;

    const tramitesFiltrados = tramites
        .filter(t =>
            !estadoFiltro || t.estado === estadoFiltro
        )
        .filter(t => {
            if (!busqueda.trim()) return true;
            const b = busqueda.trim().toLowerCase();
            return (
                t.numero_referencia?.toLowerCase().includes(b) ||
                t.asunto?.toLowerCase().includes(b) ||
                nombreArea(t.area_origen_id)?.toLowerCase().includes(b) ||
                nombreArea(t.area_destino_id)?.toLowerCase().includes(b) ||
                t.estado?.toLowerCase().includes(b)
            );
        });

    return (
        <div className="tramites-internos-page">
            <h2>Trámites Internos</h2>
            <div className="toolbar-tramites-in">
                <button className="btn-crear" onClick={() => setFormVisible(!formVisible)}>
                    <FaPlusCircle /> {formVisible ? "Cancelar" : "Nuevo Trámite Interno"}
                </button>
                <button className="btn-crear" onClick={fetchTramites}><FaSync /> Refrescar</button>

                <select
                    value={estadoFiltro}
                    onChange={e => setEstadoFiltro(e.target.value)}
                    style={{ marginLeft: 16, padding: "5px 12px" }}
                >
                    <option value="">Todos los estados</option>
                    <option value="pendiente">Pendiente</option>
                    <option value="derivado">Derivado</option>
                    <option value="recibido">Recibido</option>
                    <option value="atendido">Atendido</option>
                    <option value="archivado">Archivado</option>
                </select>

                <input
                    type="text"
                    placeholder="Buscar trámite..."
                    value={busqueda}
                    onChange={e => setBusqueda(e.target.value)}
                    style={{ marginLeft: 16, padding: "5px 12px", minWidth: 180 }}
                />
            </div>
            {formVisible && (
                <form className="form-tramite-interno" onSubmit={handleSubmit}>
                    <div>
                        <label>Referencia:</label>
                        <input name="numero_referencia" value={form.numero_referencia} onChange={handleFormChange} required />
                    </div>
                    <div>
                        <label>Asunto:</label>
                        <input name="asunto" value={form.asunto} onChange={handleFormChange} required />
                    </div>
                    <div>
                        <label>Contenido:</label>
                        <textarea name="contenido" value={form.contenido} onChange={handleFormChange} required />
                    </div>
                    <div>
                        <label>Folios:</label>
                        <input name="folios" type="number" min={1} value={form.folios} onChange={handleFormChange} />
                    </div>
                    <div>
                        <label>Área Destino:</label>
                        <select name="area_destino_id" value={form.area_destino_id} onChange={handleFormChange} required>
                            <option value="">Seleccione área</option>
                            {areas.map(a => <option value={a.id} key={a.id}>{a.nombre}</option>)}
                        </select>
                    </div>
                    <div>
                        <label>Adjuntar PDF:</label>
                        <input name="archivo" type="file" accept="application/pdf" ref={fileInputFormRef} onChange={handleFormChange} />
                    </div>
                    <div>
                        <label>Prioridad:</label>
                        <input name="prioridad" type="number" min={1} max={5} value={form.prioridad} onChange={handleFormChange} />
                    </div>
                    <button type="submit" className="btn-crear">Crear</button>
                </form>
            )}
            {(success || error) && (
                <div className={success ? "success" : "error"}>{success || error}</div>
            )}
            {loading ? (
                <div className="loading">Cargando trámites internos...</div>
            ) : error ? (
                <div className="error">{error}</div>
            ) : (
                <table>
                    <thead>
                        <tr>
                            <th>N°</th>
                            <th>Referencia</th>
                            <th>Asunto</th>
                            <th>Área Origen</th>
                            <th>Área Destino</th>
                            <th>Estado</th>
                            <th>Fecha Envío</th>
                            <th>PDF</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tramitesFiltrados.length === 0 ? (
                            <tr>
                                <td colSpan={9}>No hay trámites internos.</td>
                            </tr>
                        ) : (
                            tramitesFiltrados.map((t, idx) => (
                                <tr key={t.id}>
                                    <td>{idx + 1}</td>
                                    <td>{t.numero_referencia}</td>
                                    <td>{t.asunto}</td>
                                    <td>{nombreArea(t.area_origen_id)}</td>
                                    <td>{nombreArea(t.area_destino_id)}</td>
                                    <td>{t.estado}</td>
                                    <td>{formatearFecha(t.fecha_envio)}</td>
                                    <td>
                                        {t.archivo ? (
                                            <button className="btn-accion" title="Ver PDF" onClick={() => verPDF(t.archivo)}>
                                                <FaFilePdf />
                                            </button>
                                        ) : "-"}
                                    </td>
                                    <td style={{ display: "flex", gap: 6 }}>
                                        <button className="btn-accion" onClick={() => abrirDetalle(t)} title="Ver Detalles">
                                            <FaEye />
                                        </button>
                                        <button className="btn-accion" style={{ background: "#ffa726", color: "#1a237e" }}
                                            onClick={() => abrirDerivar(t)} title="Derivar Trámite">
                                            <FaShareSquare />
                                        </button>
                                        <button className="btn-accion" style={{ background: "#27ae60", color: "#fff" }}
                                            onClick={() => abrirContestar(t)} title="Contestar/Atender">
                                            <FaReply />
                                        </button>
                                        {puedeRecibir(t) && (
                                            <button className="btn-accion" style={{ background: "#1976d2", color: "#fff" }}
                                                onClick={() => recibirTramite(t)}
                                                title="Marcar como recibido">
                                                <FaCheck />
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            )}

            {/* MODAL PDF */}
            {modalPDF.mostrar && (
                <div className="modal-bg-pdf" onClick={() => setModalPDF({ mostrar: false, url: "" })}>
                    <div className="modal-pdf-viewer" style={{ maxWidth: "1100px", width: "92vw", minHeight: "70vh", height: "auto" }} onClick={e => e.stopPropagation()}>
                        <iframe
                            src={modalPDF.url}
                            title="PDF"
                            width="100%"
                            height="700px"
                            style={{ border: 0, display: "block", borderRadius: "14px 14px 0 0" }}
                        />
                        <button className="btn-modal cerrar" onClick={() => setModalPDF({ mostrar: false, url: "" })}>Cerrar PDF</button>
                    </div>
                </div>
            )}

            {/* MODAL DETALLE + HISTORIAL */}
            {modal && tramiteSel && (
                <div className="modal-bg">
                    <div className="modal-tramite-detalle">
                        <h3>Detalle de Trámite Interno</h3>
                        <div><b>N°:</b> {tramites.findIndex(x => x.id === tramiteSel.id) + 1}</div>
                        <div><b>Referencia:</b> {tramiteSel.numero_referencia}</div>
                        <div><b>Asunto:</b> {tramiteSel.asunto}</div>
                        <div><b>Área Origen:</b> {nombreArea(tramiteSel.area_origen_id)}</div>
                        <div><b>Área Destino:</b> {nombreArea(tramiteSel.area_destino_id)}</div>
                        <div><b>Estado:</b> {tramiteSel.estado}</div>
                        <div><b>Fecha Envío:</b> {formatearFecha(tramiteSel.fecha_envio)}</div>
                        <div style={{ marginTop: 18 }}>
                            <b>Historial / Seguimiento:</b>
                            <ol>
                                {seguimiento.length === 0 ? (
                                    <li>No hay movimientos registrados.</li>
                                ) : seguimiento.map((mov) => (
                                    <li key={mov.id}>
                                        <b>{mov.accion}:</b> {mov.descripcion} <i>({formatearFecha(mov.fecha_hora)})</i>
                                        {mov.adjunto && (
                                            <button className="btn-accion" onClick={() => verPDF(mov.adjunto)} title="Ver PDF Adjunto">
                                                <FaFilePdf />
                                            </button>
                                        )}
                                    </li>
                                ))}
                            </ol>
                        </div>
                        <div style={{ marginTop: 8 }}>
                            <button className="btn-modal cerrar" onClick={() => setModal(false)}>
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* MODAL DERIVAR */}
            {modalDerivar && tramiteSel && (
                <div className="modal-bg">
                    <div className="modal-tramite-detalle">
                        <h3>Derivar Trámite Interno</h3>
                        <form onSubmit={derivarTramite} style={{ marginTop: 15 }}>
                            <label>Área destino:</label>
                            <select
                                value={areaDerivar}
                                onChange={e => setAreaDerivar(e.target.value)}
                                required
                                style={{ width: "100%", padding: 7, marginBottom: 11 }}
                            >
                                <option value="">Seleccione área</option>
                                {areas
                                    .filter(a => a.id !== tramiteSel.area_destino_id)
                                    .map(a => (
                                        <option value={a.id} key={a.id}>{a.nombre}</option>
                                    ))}
                            </select>
                            <button className="btn-modal" style={{ background: "#ffa726", color: "#1a237e" }}
                                type="submit" disabled={loading || !areaDerivar}>
                                <FaShareSquare /> Derivar
                            </button>
                            <button className="btn-modal cerrar" type="button" onClick={() => setModalDerivar(false)} style={{ marginLeft: 10 }}>
                                Cancelar
                            </button>
                            {successMsg && <span className="success">{successMsg}</span>}
                            {errorMsg && <span className="error">{errorMsg}</span>}
                        </form>
                    </div>
                </div>
            )}

            {/* MODAL CONTESTAR */}
            {modalContestar && tramiteSel && (
                <div className="modal-bg">
                    <div className="modal-tramite-detalle">
                        <h3>Contestar Trámite Interno</h3>
                        <form onSubmit={contestarTramite}>
                            <textarea
                                value={respuesta}
                                onChange={e => setRespuesta(e.target.value)}
                                placeholder="Escribe tu respuesta aquí..."
                                rows={3}
                                style={{ width: "100%" }}
                            />
                            <div className="adjuntar-box">
                                <label htmlFor="pdfRespuesta" className="btn-adjuntar">
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
                                    <span>
                                        <FaFilePdf style={{ color: "#d32f2f" }} />
                                        {pdfRespuesta.name}
                                        <button
                                            type="button"
                                            className="btn-cancelar-adjunto"
                                            onClick={() => { setPdfRespuesta(null); fileInputRef.current.value = ""; }}
                                        >x</button>
                                    </span>
                                )}
                            </div>
                            <button className="btn-modal atender" type="submit"
                                disabled={loading || (!respuesta.trim() && !pdfRespuesta)}
                                style={{ marginTop: 10 }}>
                                <FaReply /> Enviar Contestación
                            </button>
                        </form>
                        <div style={{ marginTop: 8 }}>
                            <button className="btn-modal cerrar" onClick={() => setModalContestar(false)}>
                                Cerrar
                            </button>
                        </div>
                        {successMsg && <span className="success">{successMsg}</span>}
                        {errorMsg && <span className="error">{errorMsg}</span>}
                    </div>
                </div>
            )}
        </div>
    );
}