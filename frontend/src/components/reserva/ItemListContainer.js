import React, { useState, useEffect } from 'react';
import ItemList from './ItemList';
import EditItemForm from './EditItemForm';
import Filter from './Filter';
import './EditItemForm.css';  // Importar el archivo CSS para el formulario de edición

const ItemListContainer = () => {
    const [items, setItems] = useState([]);
    const [filteredItems, setFilteredItems] = useState([]);
    const [editingItem, setEditingItem] = useState(null);
    const [message, setMessage] = useState('');  // Estado para manejar mensajes de éxito o error
    const [messageType, setMessageType] = useState('');  // Estado para manejar el tipo de mensaje
    const [users, setUsers] = useState([]);  // Estado para manejar la lista de usuarios
    const [mesas, setMesas] = useState([]);  // Estado para manejar la lista de mesas

    useEffect(() => {
        fetch('http://localhost:3100/reservas')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const reservas = data.data.map(reserva => ({
                        id: reserva[0],
                        fecha: reserva[1],
                        hora: reserva[2],
                        estado: reserva[3],
                        detalle: reserva[4],
                        usuario_responsable: reserva[5],
                        numero_mesa: reserva[6]
                    }));
                    const sortedItems = reservas.sort((a, b) => b.id - a.id);
                    setItems(sortedItems);
                    setFilteredItems(sortedItems);  // Inicialmente mostrar todos los items
                } else {
                    console.error('Error fetching reservations:', data.message);
                }
            })
            .catch(error => console.error('Error:', error));
    }, []);

    useEffect(() => {
        fetch('http://localhost:3200/users')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    setUsers(data.data);
                } else {
                    console.error('Error fetching users:', data.message);
                }
            })
            .catch(error => console.error('Error:', error));
    }, []);

    useEffect(() => {
        fetch('http://localhost:3300/mesas')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    setMesas(data.data);
                } else {
                    console.error('Error fetching mesas:', data.message);
                }
            })
            .catch(error => console.error('Error:', error));
    }, []);

    const handleEdit = (item) => {
        setEditingItem(item);
        setMessage('');  // Limpiar mensaje al comenzar la edición
        setMessageType('');
    };

    const handleDelete = (item) => {
        fetch(`http://localhost:3100/delete_reserva/${item.id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const updatedItems = items.filter(i => i.id !== item.id).sort((a, b) => b.id - a.id);
                setItems(updatedItems);
                setFilteredItems(updatedItems);
                setMessage('Reserva eliminada con éxito');  // Mostrar mensaje de éxito
                setMessageType('success');
                setTimeout(() => {
                    setMessage('');
                    setMessageType('');
                }, 3000);  // Ocultar mensaje después de 3 segundos
            } else {
                setMessage(data.message);  // Mostrar mensaje de error si ocurre un problema
                setMessageType('error');
                console.error('Error deleting reservation:', data.message);
                setTimeout(() => {
                    setMessage('');
                    setMessageType('');
                }, 3000);  // Ocultar mensaje después de 3 segundos
            }
        })
        .catch(error => {
            setMessage('An error occurred while deleting the reservation. Please try again.');
            setMessageType('error');
            console.error('Error:', error);
            setTimeout(() => {
                setMessage('');
                setMessageType('');
            }, 3000);  // Ocultar mensaje después de 3 segundos
        });
    };

    const handleSave = (updatedItem) => {
        const method = updatedItem.id ? 'PUT' : 'POST';
        const url = updatedItem.id ? `http://localhost:3100/update_reserva/${updatedItem.id}` : 'http://localhost:3100/create_reserva';
    
        fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updatedItem),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const newReserva = {
                    id: data.data[0],
                    fecha: data.data[1],
                    hora: data.data[2],
                    estado: data.data[3],
                    detalle: data.data[4],
                    usuario_responsable: data.data[5],
                    numero_mesa: data.data[6]
                };
                const updatedItems = method === 'PUT'
                    ? items.map(item => (item.id === updatedItem.id ? newReserva : item)).sort((a, b) => b.id - a.id)
                    : [newReserva, ...items].sort((a, b) => b.id - a.id);
                setItems(updatedItems);
                setFilteredItems(updatedItems);
                setEditingItem(null);
                setMessage(updatedItem.id ? 'Reserva actualizada con éxito' : 'Reserva creada con éxito');  // Mostrar mensaje de éxito
                setMessageType('success');
                setTimeout(() => {
                    setMessage('');
                    setMessageType('');
                }, 3000);  // Ocultar mensaje después de 3 segundos
            } else {
                setMessage(data.message);  // Mostrar mensaje de error si ocurre un problema
                setMessageType('error');
                console.error(`Error ${method === 'PUT' ? 'updating' : 'creating'} reservation:`, data.message);
                setTimeout(() => {
                    setMessage('');
                    setMessageType('');
                }, 3000);  // Ocultar mensaje después de 3 segundos
            }
        })
        .catch(error => {
            setMessage(`An error occurred while ${method === 'PUT' ? 'updating' : 'creating'} the reservation. Please try again.`);
            setMessageType('error');
            console.error('Error:', error);
            setTimeout(() => {
                setMessage('');
                setMessageType('');
            }, 3000);  // Ocultar mensaje después de 3 segundos
        });
    };

    const handleFilter = (filters) => {
        const filtered = items.filter(item => {
            const matchFecha = filters.fecha ? item.fecha === filters.fecha : true;
            const matchHora = filters.hora ? item.hora === filters.hora : true;
            const matchEstado = filters.estado ? item.estado === filters.estado : true;
            const matchDetalle = filters.detalle ? item.detalle.includes(filters.detalle) : true;
            const matchUsuario = filters.usuario_responsable ? item.usuario_responsable == filters.usuario_responsable : true;
            const matchMesa = filters.numero_mesa ? item.numero_mesa == filters.numero_mesa : true;
            return matchFecha && matchHora && matchEstado && matchDetalle && matchUsuario && matchMesa;
        });
        setFilteredItems(filtered);
    };

    return (
        <div className="item-list-container">
            <h1>Item List</h1>
            {message && (
                <div className={`message ${messageType === 'error' ? 'error-message' : 'success-message'}`}>
                    {message}
                </div>
            )}  {/* Mostrar mensaje de éxito o error */}
            <button className="floating-button" onClick={() => setEditingItem({})}>+</button>
            <Filter onFilter={handleFilter} users={users} mesas={mesas} />
            {editingItem ? (
                <EditItemForm item={editingItem} onSave={handleSave} onCancel={() => setEditingItem(null)} users={users} mesas={mesas} />
            ) : (
                <ItemList items={filteredItems} onEdit={handleEdit} onDelete={handleDelete} />
            )}
        </div>
    );
};

export default ItemListContainer;
