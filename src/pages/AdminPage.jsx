import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { socialService } from "../services/socialService";

function AdminPage() {
  const { user } = useAuth();
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (user?.role !== "admin") {
      return;
    }
    socialService
      .getAdminOverview()
      .then((response) => setOverview(response.data.data))
      .catch((loadError) => setError(loadError.response?.data?.message || "Failed to load admin panel."));
  }, [user?.role]);

  if (user?.role !== "admin") {
    return <div className="panel">Admin access is required for this page.</div>;
  }

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (!overview) {
    return <div className="panel">Loading admin overview...</div>;
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h3>Platform activity</h3>
      </div>
      <div className="stat-grid">
        <article>
          <span className="tiny-text">Users</span>
          <strong>{overview.user_count}</strong>
        </article>
        <article>
          <span className="tiny-text">Schools</span>
          <strong>{overview.school_count}</strong>
        </article>
        <article>
          <span className="tiny-text">Clubs</span>
          <strong>{overview.club_count}</strong>
        </article>
        <article>
          <span className="tiny-text">Posts</span>
          <strong>{overview.post_count}</strong>
        </article>
      </div>
    </section>
  );
}

export default AdminPage;
