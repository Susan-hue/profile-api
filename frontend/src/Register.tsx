import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register, setToken, ApiError } from "./api";
import "./Login.css";

export default function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setFieldErrors({});
    setLoading(true);

    try {
      const { token } = await register(username, email, password, displayName || undefined);
      setToken(token);
      navigate("/", { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.status === 400) {
        const body = err.body as Record<string, string[]> | undefined;
        if (body) {
          const fieldErrs: Record<string, string> = {};
          for (const [key, val] of Object.entries(body)) {
            fieldErrs[key] = Array.isArray(val) ? val[0] : String(val);
          }
          setFieldErrors(fieldErrs);
        } else {
          setError("Invalid input. Please check your details.");
        }
      } else {
        setError("Unable to reach the server. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <h1 className="login-title">New Record</h1>
          <p className="login-subtitle">Create a personal records file</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="login-field">
            <label htmlFor="reg-username" className="login-label">
              Username
            </label>
            <input
              id="reg-username"
              type="text"
              className="login-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
              disabled={loading}
            />
            {fieldErrors.username && (
              <span className="field-error">{fieldErrors.username}</span>
            )}
          </div>

          <div className="login-field">
            <label htmlFor="reg-email" className="login-label">
              Email
            </label>
            <input
              id="reg-email"
              type="email"
              className="login-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              disabled={loading}
            />
            {fieldErrors.email && (
              <span className="field-error">{fieldErrors.email}</span>
            )}
          </div>

          <div className="login-field">
            <label htmlFor="reg-display-name" className="login-label">
              Full Name
            </label>
            <input
              id="reg-display-name"
              type="text"
              className="login-input"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Optional"
              autoComplete="name"
              disabled={loading}
            />
          </div>

          <div className="login-field">
            <label htmlFor="reg-password" className="login-label">
              Password
            </label>
            <input
              id="reg-password"
              type="password"
              className="login-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              autoComplete="new-password"
              disabled={loading}
            />
            {fieldErrors.password && (
              <span className="field-error">{fieldErrors.password}</span>
            )}
          </div>

          {error && <p className="login-error">{error}</p>}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? "Creating..." : "Create account"}
          </button>
        </form>

        <p className="login-link">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
