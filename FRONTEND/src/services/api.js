// src/services/api.js

const API_URL = import.meta.env.VITE_API_URL;

export const pingBackend = async () => {
    const response = await fetch(`${API_URL}/ping`);
    return response.json();
};
