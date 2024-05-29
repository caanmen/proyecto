import React, { useState, useEffect } from 'react';
import './EditItemForm.css';  // Importar el archivo CSS para el formulario de edición

const EditItemForm = ({ item, onSave, onCancel, users, mesas }) => {
    const [formData, setFormData] = useState({ ...item });
    const [errors, setErrors] = useState({});
    const estadoOptions = ['confirmado', 'cancelado', 'disponible'];
    const [timeOptions, setTimeOptions] = useState([]);

    useEffect(() => {
        // Set default values if not set
        if (users.length > 0 && !formData.usuario_responsable) {
            setFormData(prevFormData => ({
                ...prevFormData,
                usuario_responsable: users[0][0]  // Default to first user
            }));
        }
        if (mesas.length > 0 && !formData.numero_mesa) {
            setFormData(prevFormData => ({
                ...prevFormData,
                numero_mesa: mesas[0][0]  // Default to first mesa
            }));
        }
        if (!formData.estado) {
            setFormData(prevFormData => ({
                ...prevFormData,
                estado: estadoOptions[0]  // Default to first estado option
            }));
        }
    }, [users, mesas, formData]);

    useEffect(() => {
        // Generate time options with 30-minute intervals
        const times = [];
        for (let hour = 0; hour < 24; hour++) {
            for (let minute = 0; minute < 60; minute += 30) {
                const time = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
                times.push(time);
            }
        }
        setTimeOptions(times);
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.fecha) {
            newErrors.fecha = 'La fecha es requerida';
        }
        if (!formData.hora) {
            newErrors.hora = 'La hora es requerida';
        }
        if (!formData.estado) {
            newErrors.estado = 'El estado es requerido';
        }
        if (!formData.detalle) {
            newErrors.detalle = 'El detalle es requerido';
        }
        if (!formData.usuario_responsable) {
            newErrors.usuario_responsable = 'El usuario responsable es requerido';
        }
        if (!formData.numero_mesa) {
            newErrors.numero_mesa = 'La mesa es requerida';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (validateForm()) {
            onSave(formData);
        }
    };

    // Obtener la fecha y hora actuales
    const today = new Date().toISOString().split('T')[0];
    const currentTime = new Date().toTimeString().split(' ')[0].slice(0, 5);

    return (
        <form onSubmit={handleSubmit} className="edit-form">
            <div className="form-group">
                <label>Fecha:</label>
                <input 
                    type="date" 
                    name="fecha" 
                    value={formData.fecha || ''} 
                    onChange={handleChange} 
                    min={today} // Deshabilitar fechas pasadas
                />
                {errors.fecha && <span className="error-message">{errors.fecha}</span>}
            </div>
            <div className="form-group">
                <label>Hora:</label>
                <select 
                    name="hora" 
                    value={formData.hora || ''} 
                    onChange={handleChange}
                >
                    <option value="" disabled>Selecciona una hora</option>
                    {timeOptions.map((time, index) => (
                        <option key={index} value={time}>{time}</option>
                    ))}
                </select>
                {errors.hora && <span className="error-message">{errors.hora}</span>}
            </div>
            <div className="form-group">
                <label>Estado:</label>
                <select 
                    name="estado" 
                    value={formData.estado || estadoOptions[0]} 
                    onChange={handleChange}
                >
                    {estadoOptions.map((estado, index) => (
                        <option key={index} value={estado}>{estado}</option>
                    ))}
                </select>
                {errors.estado && <span className="error-message">{errors.estado}</span>}
            </div>
            <div className="form-group">
                <label>Detalle:</label>
                <input 
                    type="text" 
                    name="detalle" 
                    value={formData.detalle || ''} 
                    onChange={handleChange} 
                />
                {errors.detalle && <span className="error-message">{errors.detalle}</span>}
            </div>
            <div className="form-group">
                <label>Usuario Responsable:</label>
                <select 
                    name="usuario_responsable" 
                    value={formData.usuario_responsable || (users.length > 0 ? users[0][0] : '')} 
                    onChange={handleChange}
                >
                    {users.map((usuario) => (
                        <option key={usuario[0]} value={usuario[0]}>{`${usuario[1]} ${usuario[2]}`}</option>
                    ))}
                </select>
                {errors.usuario_responsable && <span className="error-message">{errors.usuario_responsable}</span>}
            </div>
            <div className="form-group">
                <label>Mesa:</label>
                <select 
                    name="numero_mesa" 
                    value={formData.numero_mesa || (mesas.length > 0 ? mesas[0][0] : '')} 
                    onChange={handleChange}
                >
                    {mesas.map((mesa) => (
                        <option key={mesa[0]} value={mesa[0]}>{`Lugar: ${mesa[2]} N Personas: ${mesa[1]}`}</option>
                    ))}
                </select>
                {errors.numero_mesa && <span className="error-message">{errors.numero_mesa}</span>}
            </div>
            <div className="form-actions">
                <button type="submit" className="save-button">Save</button>
                <button type="button" onClick={onCancel} className="cancel-button">Cancel</button>
            </div>
        </form>
    );
};

export default EditItemForm;
