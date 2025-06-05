// src/services/areaService.js
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function obtenerAreas() {
    const res = await fetch(`${API_URL}/areas`);
    if (!res.ok) throw new Error("Error al obtener áreas");
    return await res.json();
}

export async function crearArea(area) {
    const res = await fetch(`${API_URL}/areas`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(area)
    });
    if (!res.ok) throw new Error("Error al crear área");
    return await res.json();
}

export async function actualizarArea(id, area) {
    const res = await fetch(`${API_URL}/areas/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(area)
    });
    if (!res.ok) throw new Error("Error al actualizar área");
    return await res.json();
}

export async function eliminarArea(id) {
    const res = await fetch(`${API_URL}/areas/${id}`, {
        method: "DELETE"
    });
    if (!res.ok) throw new Error("Error al eliminar área");
    return await res.json();
}