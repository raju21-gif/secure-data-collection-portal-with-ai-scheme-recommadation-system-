import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    // Verify token and get fresh user data
                    const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/me`, {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    if (response.ok) {
                        const userData = await response.json();
                        setUser(userData);
                        localStorage.setItem('user', JSON.stringify(userData));
                    } else {
                        // Token invalid or expired
                        logout();
                    }
                } catch (error) {
                    console.error("Auth check failed:", error);
                    // Keep existing user from local storage as fallback or logout? 
                    // Safer to maybe logout or just do nothing if network error.
                    // For now, let's keep the localStorage user if network fails, but if server says 401, we logout.
                }
            }
            setLoading(false);
        };

        checkAuth();
    }, []);

    const login = (userData, token) => {
        // MANUAL ADMIN CHECK
        // Check if this is a manual login attempt with admin credentials
        // Note: In a real app, this should be done on the backend. This is for the requested manual mode.
        if (userData?.email === 'admin@freedy.ai' && userData?.password === 'admin123') {
            const adminUser = {
                ...userData,
                role: 'admin',
                name: 'System Admin',
                id: 'admin-001'
            };
            setUser(adminUser);
            localStorage.setItem('user', JSON.stringify(adminUser));
            // No token needed for this manual local mode, or set a dummy one
            localStorage.setItem('token', 'manual-admin-token');
            return true; // Indicate success
        }

        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        if (token) {
            localStorage.setItem('token', token);
        }
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
    };

    const value = {
        user,
        login,
        logout,
        loading,
        isAuthenticated: !!user
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
