// RUTA: src/services/tramitesInternosService.js

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function obtenerTramitesInternos(usuarioLogueado) {
    const rol = usuarioLogueado.rol;
    const area_id = usuarioLogueado.area_id;
    const url = `${API_URL}/tramites-internos?rol=${rol}&area_id=${area_id}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("No se pudo obtener trámites internos");
    const data = await res.json();
    return data.tramites || [];
}

export async function crearTramiteInterno(datos) {
    const res = await fetch(`${API_URL}/tramites-internos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos)
    });
    if (!res.ok) throw new Error("Error al crear trámite interno");
    return res.json();
}

export async function eliminarTramiteInterno(id) {
    const res = await fetch(`${API_URL}/tramites-internos/${id}`, {
        method: "DELETE"
    });
    if (!res.ok) throw new Error("Error al eliminar trámite interno");
    return res.json();
}