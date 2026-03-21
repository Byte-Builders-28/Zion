// Global configuration for ZION frontend
const config = {
  // Backend server base URL - will be set dynamically
  BACKEND_BASE_URL: 'http://localhost:8000',
  
  // API endpoints
  API_ENDPOINTS: {
    DASHBOARD_STATS: '/dashboard/stats',
    THREATS: '/threats',
    DASHBOARD: '/dashboard',
    POLICIES: '/policies',
    SIMULATION: '/simulation',
    LOGS: '/logs'
  },
  
  // Application settings
  APP_NAME: 'ZION',
  VERSION: '1.0.0',
  
  // Matrix rain settings
  MATRIX_RAIN: {
    OPACITY: 0.45,
    COLORS: ['#0F0', '#F00', '#0AF', '#FF0']
  }
};

// Export for use throughout the application
export default config;

// Also export individual constants for convenience
export const BACKEND_BASE_URL = config.BACKEND_BASE_URL;
export const API_ENDPOINTS = config.API_ENDPOINTS;
