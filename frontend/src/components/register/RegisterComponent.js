import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './RegisterComponent.css';

const RegisterComponent = () => {
    const [nombre, setNombre] = useState('');
    const [apellido, setApellido] = useState('');
    const [correo, setCorreo] = useState('');
    const [telefono, setTelefono] = useState('');
    const [tipoUsuario, setTipoUsuario] = useState('');
    const [contrasena, setContrasena] = useState('');
    const navigate = useNavigate();

    const handleRegister = (e) => {
        e.preventDefault();
        fetch('http://localhost:3200/create_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                nombre, 
                apellido, 
                correo, 
                telefono, 
                tipo_usuario: tipoUsuario, 
                contrasena 
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'error') {
                console.error('Error:', data.message);
            } else {
                console.log('Success:', data.message);
                navigate('/items');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    };

    const handleNavigateToLogin = () => {
        navigate('/');
    };

    return (
        <div className="register-container">
            <h2>Register</h2>
            <form onSubmit={handleRegister}>
                <div className="form-group">
                    <label htmlFor="nombre">Nombre:</label>
                    <input
                        type="text"
                        id="nombre"
                        value={nombre}
                        onChange={(e) => setNombre(e.target.value)}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="apellido">Apellido:</label>
                    <input
                        type="text"
                        id="apellido"
                        value={apellido}
                        onChange={(e) => setApellido(e.target.value)}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="correo">Correo:</label>
                    <input
                        type="email"
                        id="correo"
                        value={correo}
                        onChange={(e) => setCorreo(e.target.value)}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="telefono">Teléfono:</label>
                    <input
                        type="tel"
                        id="telefono"
                        value={telefono}
                        onChange={(e) => setTelefono(e.target.value)}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="tipoUsuario">Tipo de Usuario:</label>
                    <input
                        type="text"
                        id="tipoUsuario"
                        value={tipoUsuario}
                        onChange={(e) => setTipoUsuario(e.target.value)}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="contrasena">Contraseña:</label>
                    <input
                        type="password"
                        id="contrasena"
                        value={contrasena}
                        onChange={(e) => setContrasena(e.target.value)}
                    />
                </div>
                <button type="submit">Register</button>
            </form>
            <button onClick={handleNavigateToLogin} className="navigate-button arrow-back-button">
                ← Back to Login
            </button>
        </div>
    );
};

export default RegisterComponent;
