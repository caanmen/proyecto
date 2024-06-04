// frontend/src/components/auditoria/AuditTable.js
import React, { useEffect, useState } from 'react';
import './AuditTable.css';

const AuditTable = () => {
    const [auditRecords, setAuditRecords] = useState([]);

    useEffect(() => {
        fetch('http://localhost:3400/auditoria')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    setAuditRecords(data.data);
                } else {
                    console.error('Error fetching audit records:', data.message);
                }
            })
            .catch(error => console.error('Error:', error));
    }, []);

    return (
        <div className="audit-table-container">
            <h2>Audit Records</h2>
            <table className="audit-table">
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Acción</th>
                        <th>Fecha y Hora</th>
                        <th>Usuario Responsable</th>
                        <th>Detalle</th>
                        <th>Tabla Afectada</th>
                    </tr>
                </thead>
                <tbody>
                    {auditRecords.map(record => (
                        <tr key={record.codigo_indexacion}>
                            <td>{record.codigo_indexacion}</td>
                            <td>{record.accion_realizada}</td>
                            <td>{record.fecha_hora}</td>
                            <td>{record.usuario_responsable}</td>
                            <td>{record.detalle}</td>
                            <td>{record.tabla_afectada}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default AuditTable;
