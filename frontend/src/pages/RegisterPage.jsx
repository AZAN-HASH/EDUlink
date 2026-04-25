import { startTransition, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    school: "",
    location: "",
    role: "student"
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await register(form);
      startTransition(() => navigate("/dashboard"));
    } catch (submitError) {
      const apiMessage = submitError.response?.data?.message;
      const apiErrors = submitError.response?.data?.errors;
      if (apiErrors && typeof apiErrors === "object") {
        const firstKey = Object.keys(apiErrors)[0];
        const firstValue = apiErrors[firstKey];
        if (Array.isArray(firstValue) && firstValue.length > 0) {
          setError(firstValue[0]);
        } else if (typeof firstValue === "string") {
          setError(firstValue);
        } else {
          setError(apiMessage || "Registration failed.");
        }
      } else {
        setError(apiMessage || "Registration failed.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <section className="auth-card">
        <p className="brand-mark">EduLink</p>
        <h1>Start building with your school community.</h1>
        <form className="stack-md" onSubmit={handleSubmit}>
          <input
            className="input"
            placeholder="Username"
            value={form.username}
            onChange={(event) => setForm((current) => ({ ...current, username: event.target.value }))}
            required
          />
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
          <p className="tiny-text">You can use any password format.</p>
          <input
            className="input"
            placeholder="School (optional)"
            value={form.school}
            onChange={(event) => setForm((current) => ({ ...current, school: event.target.value }))}
          />
          <input
            className="input"
            placeholder="Location"
            value={form.location}
            onChange={(event) => setForm((current) => ({ ...current, location: event.target.value }))}
            required
          />
          <select
            className="input"
            value={form.role}
            onChange={(event) => setForm((current) => ({ ...current, role: event.target.value }))}
          >
            <option value="student">Student</option>
            <option value="club_leader">Club leader</option>
          </select>
          {error ? <p className="error-text">{error}</p> : null}
          <button className="button-primary" type="submit" disabled={submitting}>
            {submitting ? "Creating..." : "Register"}
          </button>
        </form>
        <p className="muted-text">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </section>
    </div>
  );
}

export default RegisterPage;
