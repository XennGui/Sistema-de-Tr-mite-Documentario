// src/components/TramitePdfSelector.jsx

import { useEffect, useState } from "react";

export default function TramitePdfSelector({
    open,
    onClose,
    apiUrl,
    usuario,
    onSelectPdf
}) {
    const [tipo, setTipo] = useState(null); 
    const [tramites, setTramites] = useState([]);
    const [loading, setLoading] = useState(false);

    //carga trámites según tipo y área
    useEffect(() => {
        if (!tipo || !open) return;
        setLoading(true);
        const endpoint = tipo === "interno"
            ? `/tramites-internos?rol=${usuario.rol}&area_id=${usuario.area_id}`
            : `/tramites-externos?rol=${usuario.rol}&area_id=${usuario.area_id}`;
        fetch(apiUrl + endpoint)
            .then(res => res.json())
            .then(data => {
                setTramites(data.tramites || []);
            })
            .finally(() => setLoading(false));
    }, [tipo, open, usuario, apiUrl]);

    if (!open) return null;

    return (
        <div className="tramite-selector-modal-bg" onClick={onClose}>
            <div className="tramite-selector-modal" onClick={e => e.stopPropagation()}>
                <button className="tramite-selector-close" onClick={onClose}>✖</button>
                <h3>Selecciona tipo de trámite</h3>
                <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
                    <button
                        className={tipo === "interno" ? "selected" : ""}
                        onClick={() => setTipo("interno")}
                    >Trámite Interno</button>
                    <button
                        className={tipo === "externo" ? "selected" : ""}
                        onClick={() => setTipo("externo")}
                    >Trámite Externo</button>
                </div>
                {tipo && (
                    <>
                        <h4>Lista de trámites ({tipo})</h4>
                        {loading && <div>Cargando trámites...</div>}
                        {!loading && tramites.length === 0 && <div>No hay trámites en tu área.</div>}
                        <ul className="tramite-list">
                            {tramites.map(tramite => (
                                tramite.archivo &&
                                <li key={tramite.id}>
                                    <button
                                        className="tramite-pdf-btn"
                                        onClick={() => {
                                            onSelectPdf({
                                                tipo,
                                                tramiteId: tramite.id,
                                                archivo: tramite.archivo,
                                                nombre: tramite.archivo.split("/").pop()
                                            });
                                            onClose();
                                        }}
                                    >
                                        <span>
                                            {tipo === "interno"
                                                ? tramite.numero_referencia || tramite.asunto
                                                : tramite.numero_expediente || tramite.asunto}
                                        </span>
                                        <span style={{ marginLeft: 13, color: "#1976d2" }}>PDF</span>
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </>
                )}
            </div>
        </div>
    );
}