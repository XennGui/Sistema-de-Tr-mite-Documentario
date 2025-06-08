// src/pages/DashboardInicio.jsx

import { useEffect, useState } from "react";
import { FaBuilding, FaUsers, FaFolderOpen, FaExchangeAlt } from "react-icons/fa";
import { Pie } from "react-chartjs-2";
import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend
} from "chart.js";
import { obtenerEstadisticasDashboard } from "../services/dashboardService";
import "../styles/DashboardInicio.css";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function DashboardInicio({ usuario }) {
    const [stats, setStats] = useState(null);
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        setCargando(true);
        obtenerEstadisticasDashboard(usuario)
            .then(setStats)
            .catch(() => setError("No se pudo cargar la información del dashboard."))
            .finally(() => setCargando(false));
    }, [usuario]);

    if (cargando) return <div className="dashboard-inicio">Cargando...</div>;
    if (error) return <div className="dashboard-inicio dashboard-error">{error}</div>;
    if (!stats) return null;

    const esAdmin = usuario.rol === "admin" || usuario.rol === "mesa_partes";
    const extEstados = stats.tramite_externo.estados;
    const intEstados = stats.tramite_interno.estados;

    const dataPieExt = {
        labels: ["Pendiente", "Atendido", "Denegado", "Derivado", "Archivado"],
        datasets: [
            {
                label: "Trámites Externos",
                data: [
                    extEstados.pendiente,
                    extEstados.atendido,
                    extEstados.denegado,
                    extEstados.derivado,
                    extEstados.archivado
                ],
                backgroundColor: [
                    "#FFA500", // pendiente - naranja brillante
                    "#00CED1", // atendido - turquesa
                    "#FF4500", // denegado - rojo anaranjado
                    "#1E90FF", // derivado - azul dodger
                    "#808080"  // archivado - gris
                ],
                borderColor: "#000000",
                borderWidth: 2,
            }
        ]
    };

    const dataPieInt = {
        labels: ["Pendiente", "Recibido", "Atendido", "Derivado", "Archivado"],
        datasets: [
            {
                label: "Trámites Internos",
                data: [
                    intEstados.pendiente,
                    intEstados.recibido,
                    intEstados.atendido,
                    intEstados.derivado,
                    intEstados.archivado
                ],
                backgroundColor: [
                    "#FFA500", // pendiente - naranja brillante
                    "#32CD32", // recibido - verde lima
                    "#00CED1", // atendido - turquesa
                    "#1E90FF", // derivado - azul dodger
                    "#808080"  // archivado - gris
                ],
                borderColor: "#000000",
                borderWidth: 2,
            }
        ]
    };

    return (
        <div className="dashboard-inicio">
            <div className="dashboard-cajas-row">
                {esAdmin && (
                    <>
                        <div className="dashboard-caja info-areas">
                            <FaBuilding className="dashboard-caja-icon" />
                            <div>
                                <div className="dashboard-caja-titulo">Áreas</div>
                                <div className="dashboard-caja-num">{stats.total_areas}</div>
                            </div>
                        </div>
                        <div className="dashboard-caja info-usuarios">
                            <FaUsers className="dashboard-caja-icon" />
                            <div>
                                <div className="dashboard-caja-titulo">Usuarios</div>
                                <div className="dashboard-caja-num">{stats.total_usuarios}</div>
                            </div>
                        </div>
                    </>
                )}
                <div className="dashboard-caja info-ext">
                    <FaFolderOpen className="dashboard-caja-icon" />
                    <div>
                        <div className="dashboard-caja-titulo">Trámites externos</div>
                        <div className="dashboard-caja-num">{stats.tramite_externo.total}</div>
                    </div>
                </div>
                <div className="dashboard-caja info-int">
                    <FaExchangeAlt className="dashboard-caja-icon" />
                    <div>
                        <div className="dashboard-caja-titulo">Trámites internos</div>
                        <div className="dashboard-caja-num">{stats.tramite_interno.total}</div>
                    </div>
                </div>
            </div>
            <div className="dashboard-graficos-superrow">
                <div className="dashboard-grafico-card2">
                    <div className="dashboard-grafico-titulo">Trámites Externos por Estado</div>
                    <div className="grafico-pie-wrapper2">
                        <Pie
                            data={dataPieExt}
                            options={{
                                plugins: { legend: { display: false } },
                                maintainAspectRatio: false,
                                elements: {
                                    arc: {
                                        borderWidth: 2,
                                        borderColor: '#000'
                                    }
                                }
                            }}
                            width={260}
                            height={260}
                        />
                    </div>
                    <div className="dashboard-grafico-leyenda">
                        {dataPieExt.labels.map((lbl, i) => (
                            <span key={lbl}>
                                <span
                                    className="leyenda-color"
                                    style={{ 
                                        background: dataPieExt.datasets[0].backgroundColor[i],
                                        border: "2px solid #000"
                                    }}
                                ></span>
                                {lbl} ({dataPieExt.datasets[0].data[i]})
                            </span>
                        ))}
                    </div>
                </div>
                <div className="dashboard-grafico-card2">
                    <div className="dashboard-grafico-titulo">Trámites Internos por Estado</div>
                    <div className="grafico-pie-wrapper2">
                        <Pie
                            data={dataPieInt}
                            options={{
                                plugins: { legend: { display: false } },
                                maintainAspectRatio: false,
                                elements: {
                                    arc: {
                                        borderWidth: 2,
                                        borderColor: '#000'
                                    }
                                }
                            }}
                            width={260}
                            height={260}
                        />
                    </div>
                    <div className="dashboard-grafico-leyenda">
                        {dataPieInt.labels.map((lbl, i) => (
                            <span key={lbl}>
                                <span
                                    className="leyenda-color"
                                    style={{ 
                                        background: dataPieInt.datasets[0].backgroundColor[i],
                                        border: "2px solid #000"
                                    }}
                                ></span>
                                {lbl} ({dataPieInt.datasets[0].data[i]})
                            </span>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
