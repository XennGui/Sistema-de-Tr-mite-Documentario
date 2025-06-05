//components/PruebaConexion.jsx

import { useEffect, useState } from "react";
import { pingBackend } from "../services/api";

export default function PruebaConexion() {
    const [mensaje, setMensaje] = useState("Cargando...");

    useEffect(() => {
        pingBackend()
            .then(data => setMensaje(data.message))
            .catch(() => setMensaje("Error de conexión"));
    }, []);

    return (
        <div>
            <h2>Estado de conexión con el backend:</h2>
            <p>{mensaje}</p>
        </div>
    );
}