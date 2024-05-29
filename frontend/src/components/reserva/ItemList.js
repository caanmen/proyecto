import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEdit, faTrash } from '@fortawesome/free-solid-svg-icons';
import './ItemList.css';

const ItemList = ({ items, onEdit, onDelete }) => {
    return (
        <div className="item-list">
            <div className="item-header">
                <span className="header-id">ID</span>
                <span className="header-fecha">Fecha</span>
                <span className="header-hora">Hora</span>
                <span className="header-estado">Estado</span>
                <span className="header-detalle">Detalle</span>
                <span className="header-usuario">Usuario Responsable</span>
                <span className="header-mesa">Número de Mesa</span>
                <span className="header-acciones">Acciones</span>
            </div>
            {items.map((item, index) => (
                <div key={index} className="item">
                    <span className="item-id">{item.id}</span>
                    <span className="item-fecha">{item.fecha}</span>
                    <span className="item-hora">{item.hora}</span>
                    <span className="item-estado">{item.estado}</span>
                    <span className="item-detalle">{item.detalle}</span>
                    <span className="item-usuario">{item.usuario_responsable}</span>
                    <span className="item-mesa">{item.numero_mesa}</span>
                    <div className="item-acciones">
                        <button onClick={() => onEdit(item)} className="edit-button">
                            <FontAwesomeIcon icon={faEdit} />
                        </button>
                        <button onClick={() => onDelete(item)} className="delete-button">
                            <FontAwesomeIcon icon={faTrash} />
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default ItemList;
