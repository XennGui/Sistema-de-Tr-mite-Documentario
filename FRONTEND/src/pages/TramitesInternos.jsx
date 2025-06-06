// RUTA: src/pages/TramitesInternos.jsx

import { useEffect, useState } from "react";
import { obtenerTramitesInternos, crearTramiteInterno, eliminarTramiteInterno } from "../services/tramitesInternosService";
import "../styles/TramitesInternos.css";

export default function TramitesInternos({ usuarioLogueado }) {
    const [tramites, setTramites] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [formVisible, setFormVisible] = useState(false);
    const [form, setForm] = useState({
        numero_referencia: "",
        asunto: "",
        contenido: "",
        folios: 1,
        archivo: "",
        remitente_id: usuarioLogueado?.id || 0,
        area_origen_id: usuarioLogueado?.area_id || 0,
        area_destino_id: "",
        prioridad: 3,
    });

    // Cargar trámites internos
    useEffect(() => {
        fetchTramites();
        // eslint-disable-next-line
    }, [usuarioLogueado]);

    const fetchTramites = async () => {
        setLoading(true);
        setError("");
        try {
            const datos = await obtenerTramitesInternos(usuarioLogueado);
            setTramites(datos);
        } catch (err) {
            setError(err.message || "Error al cargar trámites internos");
        }
        setLoading(false);
    };

    const handleChange = e => {
        setForm({
            ...form,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        try {
            await crearTramiteInterno(form);
            setFormVisible(false);
            setForm({
                numero_referencia: "",
                asunto: "",
                contenido: "",
                folios: 1,
                archivo: "",
                remitente_id: usuarioLogueado?.id || 0,
                area_origen_id: usuarioLogueado?.area_id || 0,
                area_destino_id: "",
                prioridad: 3,
            });
            fetchTramites();
        } catch (err) {
            setError(err.message || "Error al crear trámite interno");
        }
        setLoading(false);
    };

    const handleEliminar = async id => {
        if (!window.confirm("¿Eliminar este trámite interno?")) return;
        setLoading(true);
        setError("");
        try {
            await eliminarTramiteInterno(id);
            fetchTramites();
        } catch (err) {
            setError(err.message || "Error al eliminar trámite interno");
        }
        setLoading(false);
    };

    return (
        <div className="tramites-internos-page">
            <h2>Trámites Internos</h2>
            <button className="btn-crear" onClick={() => setFormVisible(!formVisible)}>
                {formVisible ? "Cancelar" : "Nuevo Trámite Interno"}
            </button>
            {formVisible && (
                <form className="form-tramite-interno" onSubmit={handleSubmit}>
                    <div>
                        <label>Referencia:</label>
                        <input name="numero_referencia" value={form.numero_referencia} onChange={handleChange} required />
                    </div>
                    <div>
                        <label>Asunto:</label>
                        <input name="asunto" value={form.asunto} onChange={handleChange} required />
                    </div>
                    <div>
                        <label>Contenido:</label>
                        <textarea name="contenido" value={form.contenido} onChange={handleChange} required />
                    </div>
                    <div>
                        <label>Folios:</label>
                        <input name="folios" type="number" min={1} value={form.folios} onChange={handleChange} />
                    </div>
                    <div>
                        <label>Área Destino (ID):</label>
                        <input name="area_destino_id" value={form.area_destino_id} onChange={handleChange} required />
                        {/* Si tienes lista de áreas puedes cambiar esto por un <select> */}
                    </div>
                    <div>
                        <label>Prioridad:</label>
                        <input name="prioridad" type="number" min={1} max={5} value={form.prioridad} onChange={handleChange} />
                    </div>
                    <button type="submit" className="btn-crear">Crear</button>
                </form>
            )}
            {loading ? (
                <div>Cargando trámites internos...</div>
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
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tramites.length === 0 ? (
                            <tr>
                                <td colSpan={8}>No hay trámites internos.</td>
                            </tr>
                        ) : (
                            tramites.map((t, idx) => (
                                <tr key={t.id}>
                                    <td>{idx + 1}</td>
                                    <td>{t.numero_referencia}</td>
                                    <td>{t.asunto}</td>
                                    <td>{t.area_origen_id}</td>
                                    <td>{t.area_destino_id}</td>
                                    <td>{t.estado}</td>
                                    <td>{t.fecha_envio ? new Date(t.fecha_envio).toLocaleString() : "-"}</td>
                                    <td>
                                        <button className="btn-eliminar" onClick={() => handleEliminar(t.id)}>Eliminar</button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            )}
        </div>
    );
}