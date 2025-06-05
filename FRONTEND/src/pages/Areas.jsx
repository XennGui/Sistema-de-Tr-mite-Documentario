// src/pages/Areas.jsx
import { useEffect, useState } from "react";
import { FaPlus, FaEdit, FaTrash } from "react-icons/fa";
import {
    obtenerAreas,
    crearArea,
    actualizarArea,
    eliminarArea,
} from "../services/areaService";
import "../styles/Areas.css";

export default function Areas() {
    const [areas, setAreas] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [modal, setModal] = useState(false);
    const [editando, setEditando] = useState(null);
    const [nombre, setNombre] = useState("");
    const [descripcion, setDescripcion] = useState("");
    const [error, setError] = useState("");
    const [busqueda, setBusqueda] = useState("");

    const cargarAreas = async () => {
        setCargando(true);
        try {
            const data = await obtenerAreas();
            setAreas(data.areas || []);
        } catch {
            setAreas([]);
        }
        setCargando(false);
    };

    useEffect(() => {
        cargarAreas();
    }, []);

    const abrirModal = (area = null) => {
        setEditando(area);
        setNombre(area ? area.nombre : "");
        setDescripcion(area ? area.descripcion : "");
        setError("");
        setModal(true);
    };

    const cerrarModal = () => {
        setModal(false);
        setEditando(null);
        setNombre("");
        setDescripcion("");
        setError("");
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!nombre.trim()) {
            setError("El nombre es obligatorio.");
            return;
        }
        setError("");
        try {
            if (editando) {
                await actualizarArea(editando.id, { nombre, descripcion });
            } else {
                await crearArea({ nombre, descripcion });
            }
            cerrarModal();
            cargarAreas();
        } catch {
            setError("Ocurrió un error al guardar.");
        }
    };

    const handleEliminar = async (id) => {
        if (window.confirm("¿Seguro que deseas eliminar esta área?")) {
            await eliminarArea(id);
            cargarAreas();
        }
    };

    const filteredAreas = areas.filter((a) =>
        a.nombre.toLowerCase().includes(busqueda.toLowerCase())
    );

    return (
        <div className="areas-contenedor">
            <div className="areas-header">
                <h2>Gestión de Áreas</h2>
                <button className="areas-btn-nuevo" onClick={() => abrirModal()}>
                    <FaPlus /> Nueva Área
                </button>
            </div>
            <div className="areas-busqueda">
                <input
                    type="text"
                    placeholder="Buscar área..."
                    value={busqueda}
                    onChange={(e) => setBusqueda(e.target.value)}
                />
            </div>
            {cargando ? (
                <div className="areas-cargando">Cargando...</div>
            ) : (
                <table className="areas-tabla">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Nombre</th>
                            <th>Descripción</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredAreas.length === 0 ? (
                            <tr>
                                <td colSpan={4}>No hay áreas registradas.</td>
                            </tr>
                        ) : (
                            filteredAreas.map((area, idx) => (
                                <tr key={area.id}>
                                    <td>{idx + 1}</td>
                                    <td>{area.nombre}</td>
                                    <td>{area.descripcion}</td>
                                    <td>
                                        <button
                                            className="areas-btn-editar"
                                            onClick={() => abrirModal(area)}
                                            title="Editar"
                                        >
                                            <FaEdit />
                                        </button>
                                        <button
                                            className="areas-btn-eliminar"
                                            onClick={() => handleEliminar(area.id)}
                                            title="Eliminar"
                                        >
                                            <FaTrash />
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            )}

            {modal && (
                <div className="areas-modal-fondo" onClick={cerrarModal}>
                    <div
                        className="areas-modal"
                        onClick={(e) => e.stopPropagation()}
                        tabIndex={-1}
                    >
                        <h3>{editando ? "Editar Área" : "Nueva Área"}</h3>
                        <form onSubmit={handleSubmit}>
                            <div className="areas-form-grupo">
                                <label>Nombre<span>*</span></label>
                                <input
                                    type="text"
                                    value={nombre}
                                    onChange={(e) => setNombre(e.target.value)}
                                    maxLength={100}
                                    required
                                    autoFocus
                                />
                            </div>
                            <div className="areas-form-grupo">
                                <label>Descripción</label>
                                <textarea
                                    value={descripcion || ""}
                                    onChange={(e) => setDescripcion(e.target.value)}
                                    rows={3}
                                    maxLength={500}
                                />
                            </div>
                            {error && <div className="areas-error">{error}</div>}
                            <div className="areas-form-botones">
                                <button
                                    type="button"
                                    className="areas-btn-cancelar"
                                    onClick={cerrarModal}
                                >
                                    Cancelar
                                </button>
                                <button type="submit" className="areas-btn-guardar">
                                    {editando ? "Guardar cambios" : "Crear área"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}