// src/services/dashboardService.js

// RUTA: src/services/dashboardService.js

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Obtiene las estadísticas para el dashboard, filtradas desde el backend según el usuario logueado.
 * @param {Object} usuario Usuario logueado con rol y area_id
 * @returns {Object} Estadísticas para el dashboard
 */
export async function obtenerEstadisticasDashboard(usuario) {
    const esAdmin = usuario.rol === "admin" || usuario.rol === "mesa_partes";
    const areaId = usuario.area_id;

    // Parámetros para filtrar desde el backend
    const params = `rol=${usuario.rol}&area_id=${areaId}`;

    // Si eres admin/mesa_partes, pide todos los datos.
    // Si eres usuario normal, el backend ya filtrará por tu área.
    const [
        areasRes,
        usuariosRes,
        extRes,
        intRes
    ] = await Promise.all([
        esAdmin ? fetch(`${API_URL}/areas`) : null,
        esAdmin ? fetch(`${API_URL}/usuarios`) : null,
        fetch(`${API_URL}/tramites-externos?${params}`),
        fetch(`${API_URL}/tramites-internos?${params}`)
    ]);

    const [
        areas,
        usuarios,
        ext,
        int
    ] = await Promise.all([
        esAdmin ? areasRes.json() : {},
        esAdmin ? usuariosRes.json() : {},
        extRes.json(),
        intRes.json()
    ]);

    // Los trámites ya vienen filtrados del backend
    const tramitesExt = ext.tramites || [];
    const tramitesInt = int.tramites || [];

    // Cuenta los estados de los trámites externos
    const estadosExt = { pendiente: 0, atendido: 0, denegado: 0, derivado: 0, archivado: 0 };
    tramitesExt.forEach(tramite => {
        if (estadosExt.hasOwnProperty(tramite.estado)) estadosExt[tramite.estado]++;
    });

    // Cuenta los estados de los trámites internos
    const estadosInt = { pendiente: 0, recibido: 0, atendido: 0, derivado: 0, archivado: 0 };
    tramitesInt.forEach(tramite => {
        if (estadosInt.hasOwnProperty(tramite.estado)) estadosInt[tramite.estado]++;
    });

    return {
        total_areas: esAdmin ? (Array.isArray(areas.areas) ? areas.areas.length : (areas.total || 0)) : undefined,
        total_usuarios: esAdmin ? (Array.isArray(usuarios.usuarios) ? usuarios.usuarios.length : (usuarios.total || 0)) : undefined,
        tramite_externo: {
            total: tramitesExt.length,
            estados: estadosExt
        },
        tramite_interno: {
            total: tramitesInt.length,
            estados: estadosInt
        }
    };
}
