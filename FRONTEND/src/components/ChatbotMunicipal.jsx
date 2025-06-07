// src/components/ChatbotMunicipal.jsx

import { useState, useRef, useEffect } from "react";
import { FaRobot, FaTimes, FaPaperPlane, FaSyncAlt, FaBroom, FaDatabase, FaMagic } from "react-icons/fa";
import "../styles/ChatbotMunicipal.css";

export default function ChatbotMunicipal({ placement = "center" }) {
    const [open, setOpen] = useState(false);
    const [pregunta, setPregunta] = useState("");
    const [chat, setChat] = useState([]);
    const [loading, setLoading] = useState(false);
    const [usarBD, setUsarBD] = useState(false);
    const [msgBot, setMsgBot] = useState("");
    const [entrenando, setEntrenando] = useState(false);

    const chatEndRef = useRef(null);
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

    const usuario = JSON.parse(localStorage.getItem("usuario") || "{}");

    useEffect(() => {
        if (open && chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [chat, open]);

    const limpiarChat = () => {
        setChat([]);
        setPregunta("");
        setMsgBot("¡Conversación limpiada!");
        setTimeout(() => setMsgBot(""), 1200);
    };

    const reentrenarModelo = async () => {
        setEntrenando(true);
        setMsgBot("Reentrenando modelo...");
        try {
            const res = await fetch(`${apiUrl}/reentrenar`, { method: "POST" });
            const data = await res.json();
            setMsgBot(data.mensaje || "¡Modelo reentrenado!");
        } catch {
            setMsgBot("Error reentrenando modelo.");
        }
        setEntrenando(false);
        setTimeout(() => setMsgBot(""), 2500);
    };

    const enviarPregunta = async (e) => {
        e.preventDefault();
        if (!pregunta.trim()) return;
        setMsgBot("");
        setChat(prev => [...prev, { pregunta, respuesta: "..." }]);
        setLoading(true);
        try {
            const res = await fetch(`${apiUrl}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    pregunta,
                    usar_bd: usarBD,
                    chat_history: chat.map(m => [m.pregunta, m.respuesta]),
                    usuario_id: usuario?.id || null,
                    usuario: usuario || null, // <-- ENVÍA TODO EL USUARIO
                }),
            });
            const data = await res.json();
            setChat(prev =>
                prev.map((m, idx) =>
                    idx === prev.length - 1 ? { ...m, respuesta: data.respuesta } : m
                )
            );
            setPregunta("");
        } catch (err) {
            setChat(prev =>
                prev.map((m, idx) =>
                    idx === prev.length - 1
                        ? { ...m, respuesta: "Error al responder. Intenta de nuevo." }
                        : m
                )
            );
        }
        setLoading(false);
    };


    const placementStyle = placement === "center"
        ? { position: "fixed", left: "50%", top: "10vh", transform: "translateX(-50%)", zIndex: 2001 }
        : { position: "fixed", right: "32px", bottom: "100px", zIndex: 2001 };

    // ... el resto de tu componente JSX (render) ...
    return (
        <>
            <button
                className={placement === "center" ? "chatbot-btn-center" : "chatbot-fab"}
                onClick={() => setOpen(true)}
            >
                <FaRobot size={26} />
                {placement === "center" && <span style={{ marginLeft: 10, fontWeight: 600 }}>Asistente IA</span>}
            </button>
            {open && (
                <div className="chatbot-modal-bg" style={{ ...placementStyle }} onClick={() => setOpen(false)}>
                    <div className="chatbot-modal-box" onClick={e => e.stopPropagation()} style={{ width: "520px", maxWidth: "96vw" }}>
                        <div className="chatbot-modal-header">
                            <FaRobot size={20} />
                            <span style={{ fontWeight: 600, marginLeft: 5 }}>Asistente Municipalidad de Yau</span>
                            <button className="chatbot-modal-close" onClick={() => setOpen(false)}>
                                <FaTimes />
                            </button>
                        </div>
                        <div className="chatbot-modal-tools">
                            <button className="chatbot-tool-btn" onClick={limpiarChat} title="Limpiar conversación">
                                <FaBroom /> Limpiar
                            </button>
                            <button className="chatbot-tool-btn" onClick={reentrenarModelo} disabled={entrenando} title="Reentrenar modelo">
                                <FaSyncAlt className={entrenando ? "spin" : ""} /> Reentrenar
                            </button>
                            <button className={`chatbot-tool-btn${usarBD ? " activo" : ""}`} onClick={() => setUsarBD(true)} title="Consultas directas a BD">
                                <FaDatabase /> Consulta BD
                            </button>
                            <button className={`chatbot-tool-btn${!usarBD ? " activo" : ""}`} onClick={() => setUsarBD(false)} title="Consulta general/IA">
                                <FaMagic /> Consulta IA
                            </button>
                        </div>
                        <div className="chatbot-modal-conv">
                            {msgBot && <div className="chatbot-modal-msg">{msgBot}</div>}
                            {chat.length === 0 && !msgBot ? (
                                <div className="chatbot-modal-placeholder">
                                    ¡Hola! Soy el asistente virtual municipal. Puedes preguntarme sobre trámites, áreas, documentos o sobre documentos PDF cargados.
                                </div>
                            ) : (
                                chat.map((m, idx) => (
                                    <div key={idx}>
                                        <div className="chatbot-q">{m.pregunta}</div>
                                        <div className="chatbot-a">{m.respuesta}</div>
                                    </div>
                                ))
                            )}
                            <div ref={chatEndRef}></div>
                        </div>
                        <form className="chatbot-modal-form" onSubmit={enviarPregunta}>
                            <input
                                value={pregunta}
                                onChange={e => setPregunta(e.target.value)}
                                placeholder={usarBD ? "Consulta estructurada a BD..." : "Escribe tu consulta a la IA..."}
                                disabled={loading || entrenando}
                                autoFocus
                            />
                            <button type="submit" disabled={loading || !pregunta.trim() || entrenando}>
                                <FaPaperPlane />
                            </button>
                        </form>
                    </div>
                </div>
            )}
        </>
    );
}