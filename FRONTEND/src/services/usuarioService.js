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