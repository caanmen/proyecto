// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LoginComponent from './components/login/LoginComponent';
import RegisterComponent from './components/register/RegisterComponent';
import ItemListContainer from './components/reserva/ItemListContainer';
import AuditTable from './components/auditoria/AuditTable';

import './App.css';

function App() {
    return (
        <Router>
            <Routes>
        
                
                <Route path="/" element={<LoginComponent />} />
                <Route path="/items" element={<ItemListContainer />} />
                <Route path="/register" element={<RegisterComponent />} />
                <Route path="/auditoria" element={<AuditTable />} />
                {/* Añadir rutas para las acciones del menú cuando se implementen */}
            </Routes>
        </Router>
    );
    
}

export default App;
