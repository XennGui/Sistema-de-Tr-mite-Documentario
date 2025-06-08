// src/pages/Home.jsx

import { useNavigate } from "react-router-dom";
import BarraSuperior from "../components/BarraSuperior";
import "../styles/Home.css";
import registrarImg from "../assets/registrar.png";
import buscarImg from "../assets/buscar.png";

export default function Home() {
    const navigate = useNavigate();

    return (
        <div className="municipio-app">
            <BarraSuperior mostrarBoton={true} />
            <main className="municipio-main">
                <div className="municipio-hero">
                    <h1 className="municipio-title">Bienvenido al portal de trámites del Municipio de Yau</h1>
                    <p > </p>
                </div>
                
                <div className="municipio-options">
                    {/* Opción Registrar Trámite */}
                    <div className="municipio-card" onClick={() => navigate("/registrar-tramite")}>
                        <div className="card-image-container">
                            <img src={registrarImg} alt="Registrar Trámite" className="card-main-image" />
                        </div>
                        <div className="card-content">
                            
                            <h3 className="card-title">Registrar Trámite</h3>
                            <p className="card-description">
                                    Complete el formulario para iniciar un nuevo trámite municipal. 
                                    Nuestro sistema le guiará paso a paso en el proceso.
                                </p>
                            <button className="municipio-btn municipio-btn-primary">
                                Iniciar
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M5 12h14M12 5l7 7-7 7"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                    
                    {/* Opción Buscar Trámite */}
                    <div className="municipio-card" onClick={() => navigate("/buscar-tramite")}>
                        <div className="card-image-container">
                            <img src={buscarImg} alt="Buscar Trámite" className="card-main-image" />
                        </div>
                        <div className="card-content">
                            <h3 className="card-title">Consultar Trámite</h3>
                            <p className="card-description">
                                    Verifique el estado actual de sus trámites ingresando el número de seguimiento. 
                                    Obtenga información en tiempo real.
                                </p>
                            <button className="municipio-btn municipio-btn-secondary">
                                Buscar
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <circle cx="11" cy="11" r="8"/>
                                    <path d="M21 21l-4.35-4.35"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
                
                <div className="municipio-footer">
                    <p>© {new Date().getFullYear()} Municipalidad - Servicio al Ciudadano</p>
                </div>
            </main>
        </div>
    );
}
