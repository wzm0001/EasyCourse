import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/global.css';
import { useAuthStore } from './store/auth';

useAuthStore.getState().loadFromStorage();
useAuthStore.getState().refreshUser();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
