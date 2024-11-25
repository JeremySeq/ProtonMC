let API_SERVER;

if (import.meta.env.MODE === 'development') {
    API_SERVER = 'http://localhost:5000';  // Local development API
} else {
    API_SERVER = window.location.origin;  // Production API
}

export default API_SERVER;
