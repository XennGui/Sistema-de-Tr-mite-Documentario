// src/pages/Usuarios.jsx

import { useEffect, useState } from "react";
import { FaPlus, FaEdit, FaTrash } from "react-icons/fa";
import {
    obtenerUsuarios,
    crearUsuario,
    actualizarUsuario,
    eliminarUsuario,
} from "../services/usuarioService";
import { obtenerAreas } from "../services/areaService";
import "../styles/Usuarios.css";

const ROLES_OPTIONS = [
    { value: "admin", label: "Administrador" },
    { value: "mesa_partes", label: "Mesa de partes" },
    { value: "usuario", label: "Jefe" },
    { value: "auxiliar", label: "Auxiliar" },
];

export default function Usuarios() {
    const [usuarios, setUsuarios] = useState([]);
    const [areas, setAreas] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [modal, setModal] = useState(false);
    const [editando, setEditando] = useState(null);
    const [form, setForm] = useState({
        nombre: "",
        area_id: "",
        username: "",
        password: "",
        email: "",
        rol: "usuario",
    });
    const [error, setError] = useState("");
    const [busqueda, setBusqueda] = useState("");

    const cargarUsuarios = async () => {
        setCargando(true);
        try {
            const data = await obtenerUsuarios();
            setUsuarios(data.usuarios || []);
        } catch {
            setUsuarios([]);
        }
        setCargando(false);
    };

    const cargarAreas = async () => {
        try {
            const data = await obtenerAreas();
            setAreas(data.areas || []);
        } catch {
            setAreas([]);
        }
    };

    useEffect(() => {
        cargarUsuarios();
        cargarAreas();
    }, []);

    const abrirModal = (usuario = null) => {
        setEditando(usuario);
        setForm(
            usuario
                ? {
                    nombre: usuario.nombre || "",
                    area_id: usuario.area_id || "",
                    username: usuario.username || "",
                    password: "",
                    email: usuario.email || "",
                    rol: usuario.rol || "usuario",
                }
                : {
                    nombre: "",
                    area_id: "",
                    username: "",
                    password: "",
                    email: "",
                    rol: "usuario",
                }
        );
        setError("");
        setModal(true);
    };

    const cerrarModal = () => {
        setModal(false);
        setEditando(null);
        setForm({
            nombre: "",
            area_id: "",
            username: "",
            password: "",
            email: "",
            rol: "usuario",
        });
        setError("");
    };

    const handleChange = (e) => {
        let { name, value } = e.target;
        if (name === "area_id") value = value === "" ? "" : parseInt(value, 10);
        setForm((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!form.nombre.trim() || !form.username.trim() || !form.email.trim() || (!editando && !form.password.trim())) {
            setError("Todos los campos obligatorios deben ser llenados.");
            return;
        }
        if (form.rol === "") {
            setError("Rol obligatorio.");
            return;
        }
        setError("");
        try {
            let usuarioActualizado = null;
            if (editando) {
                const { password, ...rest } = form;
                const payload = password.trim() ? { ...rest, password } : rest;
                const respuesta = await actualizarUsuario(editando.id, payload);
                usuarioActualizado = respuesta.usuario;
            } else {
                const respuesta = await crearUsuario(form);
                usuarioActualizado = respuesta.usuario;
            }

            const usuarioLogueado = JSON.parse(localStorage.getItem("usuario") || "{}");
            if (editando && usuarioActualizado && usuarioActualizado.id === usuarioLogueado.id) {
                localStorage.setItem("usuario", JSON.stringify({
                    ...usuarioLogueado,
                    ...usuarioActualizado
                }));
            }

            cerrarModal();
            cargarUsuarios();
        } catch {
            setError("Ocurrió un error al guardar.");
        }
    };

    const handleEliminar = async (id) => {
        if (window.confirm("¿Seguro que deseas eliminar este usuario?")) {
            await eliminarUsuario(id);
            cargarUsuarios();
        }
    };

    const filteredUsuarios = usuarios.filter(
        (u) =>
            u.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
            u.username.toLowerCase().includes(busqueda.toLowerCase()) ||
            u.email.toLowerCase().includes(busqueda.toLowerCase())
    );

    return (
        <div className="usuarios-contenedor">
            <div className="usuarios-header">
                <h2>Gestión de Usuarios</h2>
                <button className="usuarios-btn-nuevo" onClick={() => abrirModal()}>
                    <FaPlus /> Nuevo Usuario
                </button>
            </div>
            <div className="usuarios-busqueda">
                <input
                    type="text"
                    placeholder="Buscar usuario..."
                    value={busqueda}
                    onChange={(e) => setBusqueda(e.target.value)}
                />
            </div>
            {cargando ? (
                <div className="usuarios-cargando">Cargando...</div>
            ) : (
                <table className="usuarios-tabla">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Nombre</th>
                            <th>Área</th>
                            <th>Usuario</th>
                            <th>Email</th>
                            <th>Rol</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredUsuarios.length === 0 ? (
                            <tr>
                                <td colSpan={7}>No hay usuarios registrados.</td>
                            </tr>
                        ) : (
                            filteredUsuarios.map((usuario, idx) => (
                                <tr key={usuario.id}>
                                    <td>{idx + 1}</td>
                                    <td>{usuario.nombre}</td>
                                    <td>
                                        {areas.find((a) => a.id === usuario.area_id)
                                            ? areas.find((a) => a.id === usuario.area_id).nombre
                                            : ""}
                                    </td>
                                    <td>{usuario.username}</td>
                                    <td>{usuario.email}</td>
                                    <td>
                                        {ROLES_OPTIONS.find((r) => r.value === usuario.rol)
                                            ? ROLES_OPTIONS.find((r) => r.value === usuario.rol).label
                                            : usuario.rol}
                                    </td>
                                    <td>
                                        <button
                                            className="usuarios-btn-editar"
                                            onClick={() => abrirModal(usuario)}
                                            title="Editar"
                                        >
                                            <FaEdit />
                                        </button>
                                        <button
                                            className="usuarios-btn-eliminar"
                                            onClick={() => handleEliminar(usuario.id)}
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
                <div className="usuarios-modal-fondo" onClick={cerrarModal}>
                    <div
                        className="usuarios-modal"
                        onClick={(e) => e.stopPropagation()}
                        tabIndex={-1}
                    >
                        <h3>{editando ? "Editar Usuario" : "Nuevo Usuario"}</h3>
                        <form onSubmit={handleSubmit}>
                            <div className="usuarios-form-grupo">
                                <label>Nombre<span>*</span></label>
                                <input
                                    type="text"
                                    name="nombre"
                                    value={form.nombre}
                                    onChange={handleChange}
                                    maxLength={100}
                                    required
                                    autoFocus
                                />
                            </div>
                            <div className="usuarios-form-grupo">
                                <label>Área</label>
                                <select
                                    name="area_id"
                                    value={form.area_id || ""}
                                    onChange={handleChange}
                                >
                                    <option value="">Seleccione área</option>
                                    {areas.map((area) => (
                                        <option key={area.id} value={area.id}>
                                            {area.nombre}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className="usuarios-form-grupo">
                                <label>Nombre de usuario<span>*</span></label>
                                <input
                                    type="text"
                                    name="username"
                                    value={form.username}
                                    onChange={handleChange}
                                    maxLength={50}
                                    required
                                />
                            </div>
                            <div className="usuarios-form-grupo">
                                <label>
                                    Contraseña{editando ? " (dejar vacío para no cambiar)" : <span>*</span>}
                                </label>
                                <input
                                    type="password"
                                    name="password"
                                    value={form.password}
                                    onChange={handleChange}
                                    maxLength={50}
                                    autoComplete="new-password"
                                    required={!editando}
                                />
                            </div>
                            <div className="usuarios-form-grupo">
                                <label>Email<span>*</span></label>
                                <input
                                    type="email"
                                    name="email"
                                    value={form.email}
                                    onChange={handleChange}
                                    maxLength={100}
                                    required
                                />
                            </div>
                            <div className="usuarios-form-grupo">
                                <label>Rol<span>*</span></label>
                                <select
                                    name="rol"
                                    value={form.rol}
                                    onChange={handleChange}
                                    required
                                >
                                    {ROLES_OPTIONS.map((r) => (
                                        <option key={r.value} value={r.value}>
                                            {r.label}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            {error && <div className="usuarios-error">{error}</div>}
                            <div className="usuarios-form-botones">
                                <button
                                    type="button"
                                    className="usuarios-btn-cancelar"
                                    onClick={cerrarModal}
                                >
                                    Cancelar
                                </button>
                                <button type="submit" className="usuarios-btn-guardar">
                                    {editando ? "Guardar cambios" : "Crear usuario"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
