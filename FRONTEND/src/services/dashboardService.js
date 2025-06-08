// src/services/dashboardService.js

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * @param {Object} usuario usuario logueado con rol y area_id
 * @returns {Object} estadísticas para el dashboard
 */
export async function obtenerEstadisticasDashboard(usuario) {
    const esAdmin = usuario.rol === "admin" || usuario.rol === "mesa_partes";
    const areaId = usuario.area_id;

    const params = `rol=${usuario.rol}&area_id=${areaId}`;

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

    const tramitesExt = ext.tramites || [];
    const tramitesInt = int.tramites || [];

    const estadosExt = { pendiente: 0, atendido: 0, denegado: 0, derivado: 0, archivado: 0 };
    tramitesExt.forEach(tramite => {
        if (estadosExt.hasOwnProperty(tramite.estado)) estadosExt[tramite.estado]++;
    });

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
