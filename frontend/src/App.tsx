import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Layout from './components/Layout';
import GraphView from './components/GraphView';
import StartHere from './components/StartHere';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<StartHere />} />
          <Route path="/graph" element={<GraphView />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
