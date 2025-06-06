// src/pages/RegistrarTramite.jsx

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { jsPDF } from "jspdf";
import { FaFilePdf, FaRegFileAlt, FaUser, FaFileAlt, FaEnvelope, FaPhone, FaIdCard, FaFileUpload } from "react-icons/fa";
import logo from "../assets/logo.png";
import "../styles/RegistrarTramite.css";

//hook para convertir imagen a base64
function useImageBase64(imagePath) {
    const [base64, setBase64] = useState("");
    useEffect(() => {
        fetch(imagePath)
            .then(res => res.blob())
            .then(blob => {
                const reader = new FileReader();
                reader.onloadend = () => setBase64(reader.result);
                reader.readAsDataURL(blob);
            });
    }, [imagePath]);
    return base64;
}

export default function RegistrarTramite() {
    const [form, setForm] = useState({
        remitente: "",
        tipo_documento: "",
        folios: 1,
        asunto: "",
        contenido: "",
        archivo: null,
        tipo_persona: "natural",
        dni_ruc: "",
        email: "",
        telefono: "",
    });
    const [mensaje, setMensaje] = useState("");
    const [cargoData, setCargoData] = useState(null);
    const [error, setError] = useState("");
    const navigate = useNavigate();
    const logoBase64 = useImageBase64(logo);

    const handleChange = (e) => {
        const { name, value, files } = e.target;
        if (name === "archivo") {
            setForm(prev => ({ ...prev, archivo: files[0] }));
        } else {
            setForm(prev => ({ ...prev, [name]: value }));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setMensaje("");
        setCargoData(null);

        if (
            !form.remitente.trim() || !form.tipo_documento.trim() ||
            !form.folios || !form.asunto.trim() ||
            !form.dni_ruc.trim() || !form.email.trim()
        ) {
            setError("Por favor complete todos los campos obligatorios.");
            return;
        }

        const formData = new FormData();
        Object.entries(form).forEach(([key, val]) => {
            if (val !== null && val !== undefined) formData.append(key, val);
        });

        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/tramites-externos/`, {
                method: "POST",
                body: formData,
            });
            const data = await res.json();
            if (res.ok) {
                setMensaje(data.mensaje);
                setCargoData(data.tramite);
            } else {
                setError(data.detail || "No se pudo registrar el trámite.");
            }
        } catch {
            setError("Error de conexión.");
        }
    };

    //PDF con logo, cabecera y tabla alineada profesional
    const handleImprimirCargo = () => {
        if (!cargoData) return;
        const doc = new jsPDF({
            orientation: "portrait",
            unit: "mm",
            format: "a4"
        });

        if (logoBase64) {
            doc.addImage(logoBase64, "PNG", 25, 1, 50, 60);
        }
        doc.setFontSize(18);
        doc.setTextColor(39, 121, 189);
        doc.text("Municipalidad de Yau", 105, 21, { align: "center" });

        doc.setFont("helvetica", "bold");
        doc.setFontSize(15);
        doc.setTextColor(40, 120, 190);
        doc.text(`CARGO Nº ${cargoData.numero_expediente}`, 105, 33, { align: "center" });

        //tabla alineada vertical
        const startX = 32, startY = 43, rowHeight = 12, labelW = 55, valueW = 88;
        const rows = [
            ["Nº expediente", cargoData.numero_expediente],
            ["Remitente", cargoData.remitente],
            ["Tipo de documento", cargoData.tipo_documento],
            ["Folios", cargoData.folios],
            ["Asunto", cargoData.asunto],
            ["Código de seguridad", cargoData.codigo_seguridad],
            ["Fecha y Hora", new Date().toLocaleString()],
            ["Correo", cargoData.email],
            ["Teléfono", cargoData.telefono || "-"]
        ];

        doc.setFont("helvetica", "normal");
        doc.setFontSize(12);
        doc.setDrawColor(39, 121, 189);
        for (let i = 0; i < rows.length; i++) {
            let y = startY + i * rowHeight;
            doc.setFillColor(i % 2 === 0 ? 245 : 235, 245, 255);
            doc.rect(startX, y, labelW, rowHeight, "F");
            doc.rect(startX + labelW, y, valueW, rowHeight, "F");
            doc.setTextColor(39, 121, 189);
            doc.text(rows[i][0] + ":", startX + 3, y + 7.6);
            doc.setTextColor(60, 60, 60);
            doc.text(String(rows[i][1]), startX + labelW + 3, y + 7.6);
        }
        doc.setDrawColor(39, 121, 189);
        doc.rect(startX, startY, labelW + valueW, rowHeight * rows.length, "S");

        //SMS
        doc.setFont("helvetica", "italic");
        doc.setFontSize(11);
        doc.setTextColor(60, 80, 130);
        doc.text(
            "Estimado usuario, recuerda que con el Nº de Expediente y el código de seguridad puedes realizar el seguimiento de tu trámite.",
            startX,
            startY + rowHeight * rows.length + 14,
            { maxWidth: labelW + valueW }
        );

        doc.save(`cargo_${cargoData.numero_expediente}.pdf`);
    };

    if (mensaje) {
        return (
            <div className="tramite-exito">
                <h2><FaRegFileAlt style={{verticalAlign: "middle"}} /> {mensaje}</h2>
                <p>
                    Puede descargar su cargo en formato PDF, así mismo puede hacer su seguimiento de sus trámites a través de esta plataforma simplemente ingresando el número de expediente y su código de seguridad.
                </p>
                <button className="registrar-tramite-btn" onClick={handleImprimirCargo}>
                    <FaFilePdf style={{verticalAlign: "middle"}} /> Imprimir cargo PDF
                </button>
                <button className="registrar-tramite-btn" onClick={() => navigate("/")}>Volver al inicio</button>
            </div>
        );
    }

    return (
        <div className="registrar-tramite-contenedor-horizontal">
            <div className="registrar-tramite-header">
                <img src={logo} alt="Logo Municipalidad de Yau" style={{width: 46, height: 46, marginRight: 12}} />
                <h2>Registrar Trámite Externo</h2>
            </div>
            <form
                className="registrar-tramite-form-horizontal"
                onSubmit={handleSubmit}
                encType="multipart/form-data"
            >
                <div className="form-row">
                    <div className="form-group">
                        <label><FaUser className="form-icon" /> Remitente*:</label>
                        <input name="remitente" value={form.remitente} onChange={handleChange} required maxLength={200} />
                    </div>
                    <div className="form-group">
                        <label><FaFileAlt className="form-icon" /> Tipo de documento*:</label>
                        <input name="tipo_documento" value={form.tipo_documento} onChange={handleChange} required maxLength={50} placeholder="Ej: Carta, Oficio" />
                    </div>
                    <div className="form-group">
                        <label><FaFileAlt className="form-icon" /> Folios*:</label>
                        <input name="folios" type="number" min={1} value={form.folios} onChange={handleChange} required />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label><FaFileAlt className="form-icon" /> Asunto*:</label>
                        <input name="asunto" value={form.asunto} onChange={handleChange} required maxLength={255} />
                    </div>
                    <div className="form-group">
                        <label><FaFileAlt className="form-icon" /> Contenido:</label>
                        <textarea name="contenido" value={form.contenido} onChange={handleChange} rows={2} maxLength={800} />
                    </div>
                    <div className="form-group">
                        <label><FaFileUpload className="form-icon" /> Archivo PDF:</label>
                        <input name="archivo" type="file" accept=".pdf" onChange={handleChange} />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label><FaUser className="form-icon" /> Tipo de Persona*:</label>
                        <select name="tipo_persona" value={form.tipo_persona} onChange={handleChange} required>
                            <option value="natural">Natural</option>
                            <option value="juridica">Jurídica</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label><FaIdCard className="form-icon" /> DNI/RUC*:</label>
                        <input name="dni_ruc" value={form.dni_ruc} onChange={handleChange} required maxLength={20} />
                    </div>
                    <div className="form-group">
                        <label><FaEnvelope className="form-icon" /> Correo electrónico*:</label>
                        <input name="email" type="email" value={form.email} onChange={handleChange} required maxLength={100} />
                    </div>
                    <div className="form-group">
                        <label><FaPhone className="form-icon" /> Teléfono:</label>
                        <input name="telefono" value={form.telefono} onChange={handleChange} maxLength={20} />
                    </div>
                </div>
                {error && <div className="registrar-tramite-error">{error}</div>}
                <div className="registrar-tramite-botones">
                    <button className="registrar-tramite-btn" type="submit">Registrar</button>
                    <button className="registrar-tramite-btn" type="button" onClick={() => navigate("/")}>Cancelar</button>
                </div>
            </form>
        </div>
    );
}