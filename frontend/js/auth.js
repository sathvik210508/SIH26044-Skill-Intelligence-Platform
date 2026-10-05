/**
 * SIH26044 — Authentication & Role State Management
 */

import { api } from './api.js';

export class AuthManager {
  constructor() {
    this.currentUser = JSON.parse(localStorage.getItem('sih_user_info') || 'null');
    this.listeners = [];
  }

  onAuthChange(callback) {
    this.listeners.push(callback);
  }

  notify() {
    this.listeners.forEach(cb => cb(this.currentUser));
  }

  getUser() {
    return this.currentUser;
  }

  getRole() {
    return this.currentUser ? this.currentUser.role : null;
  }

  isAuthenticated() {
    return !!this.currentUser && !!api.getToken();
  }

  async demoLogin(role) {
    try {
      const data = await api.post(`/api/auth/demo-login/${role}`);
      api.setToken(data.access_token);
      this.currentUser = {
        id: data.user_id,
        full_name: data.full_name,
        email: data.email,
        role: data.role
      };
      localStorage.setItem('sih_user_info', JSON.stringify(this.currentUser));
      this.notify();
      return this.currentUser;
    } catch (err) {
      console.error('Demo login failed:', err);
      throw err;
    }
  }

  async login(email, password) {
    const data = await api.post('/api/auth/login', { email, password });
    api.setToken(data.access_token);
    this.currentUser = {
      id: data.user_id,
      full_name: data.full_name,
      email: data.email,
      role: data.role
    };
    localStorage.setItem('sih_user_info', JSON.stringify(this.currentUser));
    this.notify();
    return this.currentUser;
  }

  async register(email, password, full_name, role) {
    const data = await api.post('/api/auth/register', { email, password, full_name, role });
    api.setToken(data.access_token);
    this.currentUser = {
      id: data.user_id,
      full_name: data.full_name,
      email: data.email,
      role: data.role
    };
    localStorage.setItem('sih_user_info', JSON.stringify(this.currentUser));
    this.notify();
    return this.currentUser;
  }

  logout() {
    api.setToken(null);
    this.currentUser = null;
    localStorage.removeItem('sih_user_info');
    this.notify();
  }
}

export const auth = new AuthManager();
