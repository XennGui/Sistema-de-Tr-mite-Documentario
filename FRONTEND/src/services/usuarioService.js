// src/services/usuarioService.js

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function loginUsuario(identificador, password) {
    try {
        const res = await fetch(`${API_URL}/usuarios/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ identificador, password }),
        });
        const data = await res.json();
        if (res.ok && data.exito) {
            return { exito: true, usuario: data.usuario };
        }
        return { exito: false, mensaje: data.detail || "Usuario o contraseña incorrectos." };
    } catch (e) {
        return { exito: false, mensaje: "No se pudo conectar al backend." };
    }
}

export async function obtenerUsuarios() {
    const res = await fetch(`${API_URL}/usuarios`);
    if (!res.ok) throw new Error("Error al obtener usuarios");
    return await res.json();
}

/**
 * @param {*} usuario 
 */
export async function crearUsuario(usuario) {
    const res = await fetch(`${API_URL}/usuarios`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(usuario),
    });
    if (!res.ok) throw new Error("Error al crear usuario");
    return await res.json();
}

/**
 * @param {*} id 
 * @param {*} usuario 
 */
export async function actualizarUsuario(id, usuario) {
    const res = await fetch(`${API_URL}/usuarios/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(usuario),
    });
    if (!res.ok) throw new Error("Error al actualizar usuario");
    return await res.json();
}

export async function eliminarUsuario(id) {
    const res = await fetch(`${API_URL}/usuarios/${id}`, {
        method: "DELETE",
    });
    if (!res.ok) throw new Error("Error al eliminar usuario");
    return await res.json();
}
