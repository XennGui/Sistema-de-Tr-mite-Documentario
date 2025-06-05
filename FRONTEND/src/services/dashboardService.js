// src/services/dashboardService.js

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function obtenerEstadisticasDashboard(usuario) {
    const esAdmin = usuario.rol === "admin" || usuario.rol === "mesa_partes";
    const areaId = usuario.area_id;

    const [areasRes, usuariosRes, extRes, intRes] = await Promise.all([
        esAdmin ? fetch(`${API_URL}/areas`) : null,
        esAdmin ? fetch(`${API_URL}/usuarios`) : null,
        fetch(`${API_URL}/tramites-externos`),
        fetch(`${API_URL}/tramites-internos`)
    ]);
    const [areas, usuarios, ext, int] = await Promise.all([
        esAdmin ? areasRes.json() : {},
        esAdmin ? usuariosRes.json() : {},
        extRes.json(),
        intRes.json()
    ]);

    // Filtrar por área si no es admin/mesa_partes
    const tramitesExt = ext.tramites || [];
    const tramitesInt = int.tramites || [];
    const tramitesExtFiltrados = esAdmin ? tramitesExt : tramitesExt.filter(t => t.area_actual_id === areaId);
    const tramitesIntFiltrados = esAdmin ? tramitesInt : tramitesInt.filter(t => t.area_destino_id === areaId);

    const estadosExt = { pendiente: 0, atendido: 0, denegado: 0, derivado: 0, archivado: 0 };
    const estadosInt = { pendiente: 0, recibido: 0, atendido: 0, derivado: 0, archivado: 0 };

    tramitesExtFiltrados.forEach(tramite => {
        if (estadosExt[tramite.estado] !== undefined) estadosExt[tramite.estado]++;
    });
    tramitesIntFiltrados.forEach(tramite => {
        if (estadosInt[tramite.estado] !== undefined) estadosInt[tramite.estado]++;
    });

    return {
        total_areas: esAdmin ? (Array.isArray(areas.areas) ? areas.areas.length : (areas.total || 0)) : undefined,
        total_usuarios: esAdmin ? (Array.isArray(usuarios.usuarios) ? usuarios.usuarios.length : (usuarios.total || 0)) : undefined,
        tramite_externo: {
            total: tramitesExtFiltrados.length,
            estados: estadosExt
        },
        tramite_interno: {
            total: tramitesIntFiltrados.length,
            estados: estadosInt
        }
    };
}