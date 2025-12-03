import { useState } from 'react'
import './Login.css'

function Login({ onLoginSuccess }) {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
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

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-header">
                    <h1>🏋️ Compensar Gym</h1>
                    <p>Sistema de Reservas</p>
                </div>

                <div className="login-content">
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

                        {error && (
                            <div className="alert alert-error">
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            className="btn btn-primary btn-large btn-block"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner-small"></span>
                                    Iniciando...
                                </>
                            ) : (
                                '🔐 Iniciar Sesión'
                            )}
                        </button>
                    </form>

                    <div className="login-footer">
                        <p>🔒 Tus credenciales se envían seguras a Compensar</p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Login
