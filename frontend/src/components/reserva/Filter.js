import React, { useState } from 'react';
import './Filter.css';  // Importar el archivo CSS para el filtro

const Filter = ({ onFilter, users, mesas }) => {
    const [filters, setFilters] = useState({
        fecha: '',
        hora: '',
        estado: '',
        detalle: '',
        usuario_responsable: '',
        numero_mesa: ''
    });

    const estadoOptions = ['confirmado', 'cancelado', 'disponible'];

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFilters({ ...filters, [name]: value });
    };

    const handleApplyFilter = () => {
        onFilter(filters);
    };

    return (
        <div className="filter-container">
            <div className="filter-row">
                <label>Fecha:</label>
                <input type="date" name="fecha" value={filters.fecha} onChange={handleChange} />
            </div>
            <div className="filter-row">
                <label>Hora:</label>
                <input type="time" name="hora" value={filters.hora} onChange={handleChange} />
            </div>
            <div className="filter-row">
                <label>Estado:</label>
                <select name="estado" value={filters.estado} onChange={handleChange}>
                    <option value="">Todos</option>
                    {estadoOptions.map((estado, index) => (
                        <option key={index} value={estado}>{estado}</option>
                    ))}
                </select>
            </div>
            <div className="filter-row">
                <label>Detalle:</label>
                <input type="text" name="detalle" value={filters.detalle} onChange={handleChange} />
            </div>
            <div className="filter-row">
                <label>Usuario Responsable:</label>
                <select name="usuario_responsable" value={filters.usuario_responsable} onChange={handleChange}>
                    <option value="">Todos</option>
                    {users.map((usuario) => (
                        <option key={usuario[0]} value={usuario[0]}>{`${usuario[1]} ${usuario[2]}`}</option>
                    ))}
                </select>
            </div>
            <div className="filter-row">
                <label>Mesa:</label>
                <select name="numero_mesa" value={filters.numero_mesa} onChange={handleChange}>
                    <option value="">Todas</option>
                    {mesas.map((mesa) => (
                        <option key={mesa[0]} value={mesa[0]}>{`Lugar: ${mesa[2]} N Personas: ${mesa[1]}`}</option>
                    ))}
                </select>
            </div>
            <div className="filter-actions">
                <button type="button" className="apply-filter-button" onClick={handleApplyFilter}>Aplicar Filtro</button>
            </div>
        </div>
    );
};

export default Filter;
