import { startTransition, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await login(form);
      startTransition(() => navigate(location.state?.from?.pathname || "/dashboard"));
    } catch (submitError) {
      setError(submitError.response?.data?.message || "Login failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <section className="auth-card">
        <p className="brand-mark">EduLink</p>
        <h1>Welcome back to your science network.</h1>
        <p className="muted-text">Collaborate on projects, follow student builders, and keep clubs active.</p>
        <form className="stack-md" onSubmit={handleSubmit}>
          <input
            className="input"
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
            required
          />
          <input
            className="input"
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
            required
          />
          {error ? <p className="error-text">{error}</p> : null}
          <button className="button-primary" type="submit" disabled={submitting}>
            {submitting ? "Signing in..." : "Login"}
          </button>
        </form>
        <p className="muted-text">
          New here? <Link to="/register">Create an account</Link>
        </p>
      </section>
    </div>
  );
}

export default LoginPage;
