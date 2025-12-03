import { useState } from 'react'
import './Login.css'

function Login({ onLoginSuccess }) {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [useCookies, setUseCookies] = useState(false)
    const [cookieJson, setCookieJson] = useState('')
    const [formData, setFormData] = useState({
        document_type: 'CC',
        document_number: '',
        password: ''
    })

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }

    const handleLogin = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        try {
            const response = await fetch(`${import.meta.env.BASE_URL}api/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData),
                credentials: 'include'
            })

            const data = await response.json()

            if (response.ok && data.success) {
                onLoginSuccess()
            } else {
                setError(data.error || 'Error al iniciar sesión. Verifica tus credenciales.')
            }
        } catch (err) {
            setError('Error de conexión. Verifica que el servidor esté corriendo.')
        } finally {
            setLoading(false)
        }
    }

    const handleCookieLogin = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        try {
            let cookies
            try {
                cookies = JSON.parse(cookieJson)
            } catch (e) {
                setError('El JSON de cookies no es válido.')
                setLoading(false)
                return
            }

            const response = await fetch(`${import.meta.env.BASE_URL}api/login_cookies`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ cookies }),
                credentials: 'include'
            })

            const data = await response.json()

            if (response.ok && data.success) {
                onLoginSuccess()
            } else {
                setError(data.error || 'Las cookies no son válidas o han expirado.')
            }
        } catch (err) {
            setError('Error de conexión. Verifica que el servidor esté corriendo.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-header">
                    <h1>🏋️ Compensar Gym</h1>
                    <p>Sistema de Reservas</p>
                </div>

                <div className="login-tabs">
                    <button
                        className={`tab-btn ${!useCookies ? 'active' : ''}`}
                        onClick={() => setUseCookies(false)}
                    >
                        Credenciales
                    </button>
                    <button
                        className={`tab-btn ${useCookies ? 'active' : ''}`}
                        onClick={() => setUseCookies(true)}
                    >
                        Cookies (Manual)
                    </button>
                </div>

                <div className="login-content">
                    {!useCookies ? (
                        <form onSubmit={handleLogin} className="login-form">
                            <div className="form-group">
                                <label>Tipo de Documento</label>
                                <select
                                    name="document_type"
                                    value={formData.document_type}
                                    onChange={handleChange}
                                    disabled={loading}
                                >
                                    <option value="CC">Cédula de Ciudadanía</option>
                                    <option value="TI">Tarjeta de Identidad</option>
                                    <option value="CE">Cédula de Extranjería</option>
                                    <option value="PAS">Pasaporte</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label>Número de Documento</label>
                                <input
                                    type="text"
                                    name="document_number"
                                    value={formData.document_number}
                                    onChange={handleChange}
                                    placeholder="Ej: 1234567890"
                                    required
                                    disabled={loading}
                                />
                            </div>

                            <div className="form-group">
                                <label>Contraseña</label>
                                <input
                                    type="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    placeholder="Tu clave de Compensar"
                                    required
                                    disabled={loading}
                                />
                            </div>

                            {error && <div className="alert alert-error">{error}</div>}

                            <button
                                type="submit"
                                className="btn btn-primary btn-large btn-block"
                                disabled={loading}
                            >
                                {loading ? 'Iniciando...' : '🔐 Iniciar Sesión'}
                            </button>
                        </form>
                    ) : (
                        <form onSubmit={handleCookieLogin} className="login-form">
                            <div className="form-group">
                                <label>Pegar JSON de Cookies</label>
                                <textarea
                                    value={cookieJson}
                                    onChange={(e) => setCookieJson(e.target.value)}
                                    placeholder='[{"name": "...", "value": "..."}]'
                                    rows="8"
                                    required
                                    disabled={loading}
                                    className="cookie-textarea"
                                />
                            </div>

                            <div className="helper-text">
                                <p>ℹ️ Usa la extensión "EditThisCookie" o copia desde DevTools.</p>
                            </div>

                            {error && <div className="alert alert-error">{error}</div>}

                            <button
                                type="submit"
                                className="btn btn-primary btn-large btn-block"
                                disabled={loading}
                            >
                                {loading ? 'Validando...' : '🍪 Iniciar con Cookies'}
                            </button>
                        </form>
                    )}

                    <div className="login-footer">
                        <p>🔒 Tus datos se envían seguros a Compensar</p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Login
