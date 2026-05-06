import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/global.css';
import { useAuthStore } from './store/auth';
import { useAppStore } from './store/app';

useAuthStore.getState().loadFromStorage();
useAuthStore.getState().refreshUser();

if (useAuthStore.getState().isAuthenticated) {
  useAppStore.getState().fetchActiveSemester();
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
