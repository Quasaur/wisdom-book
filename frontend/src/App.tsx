import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Layout from './components/Layout';
import GraphView from './components/GraphView';
import StartHere from './components/StartHere';
import Topics from './components/Topics';
import Thoughts from './components/Thoughts';
import Quotes from './components/Quotes';
import Bible from './components/Bible';
import Tags from './components/Tags';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<StartHere />} />
          <Route path="/topics" element={<Topics />} />
          <Route path="/thoughts" element={<Thoughts />} />
          <Route path="/quotes" element={<Quotes />} />
          <Route path="/bible" element={<Bible />} />
          <Route path="/tags" element={<Tags />} />
          <Route path="/graph" element={<GraphView />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
