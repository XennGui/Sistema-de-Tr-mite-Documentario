// src/pages/Home.jsx
import { useNavigate } from "react-router-dom";
import BarraSuperior from "../components/BarraSuperior";
import "../styles/Home.css";

export default function Home() {
    const navigate = useNavigate();

    return (
        <div>
            <BarraSuperior mostrarBoton={true} />
            <main className="home-main">
                <div className="home-center-buttons">
                    <button
                        className="home-main-btn"
                        onClick={() => navigate("/registrar-tramite")}
                    >
                        Registrar Trámite
                    </button>
                    <button
                        className="home-main-btn"
                        onClick={() => navigate("/buscar-tramite")}
                    >
                        Buscar Trámite
                    </button>
                </div>
            </main>
        </div>
    );
}