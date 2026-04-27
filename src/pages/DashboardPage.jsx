import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { socialService } from "../services/socialService";

function DashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    socialService
      .getDashboard()
      .then((response) => setDashboard(response.data.data))
      .catch((loadError) => setError(loadError.response?.data?.message || "Failed to load dashboard."));
  }, []);

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (!dashboard) {
    return <div className="panel">Loading dashboard...</div>;
  }

  return (
    <div className="stack-lg">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">Recent activity</p>
          <h2>{dashboard.user.username}'s collaboration hub</h2>
        </div>
        <div className="stat-grid">
          <article>
            <span className="tiny-text">Joined clubs</span>
            <strong>{dashboard.joined_clubs.length}</strong>
          </article>
          <article>
            <span className="tiny-text">Projects posted</span>
            <strong>{dashboard.user.projects_posted}</strong>
          </article>
          <article>
            <span className="tiny-text">Unread</span>
            <strong>{dashboard.unread_notifications}</strong>
          </article>
        </div>
      </section>

      <section className="two-column">
        <div className="panel">
          <div className="panel-header">
            <h3>Your clubs</h3>
            <Link to="/search">Explore</Link>
          </div>
          <div className="stack-sm">
            {dashboard.joined_clubs.length === 0 ? (
              <p className="muted-text">You have not joined any clubs yet.</p>
            ) : (
              dashboard.joined_clubs.map((club) => (
                <Link key={club.id} className="list-row" to={`/clubs/${club.id}`}>
                  <strong>{club.name}</strong>
                </Link>
              ))
            )}
          </div>
        </div>
        <div className="panel">
          <div className="panel-header">
            <h3>Recent notifications</h3>
          </div>
          <div className="stack-sm">
            {dashboard.notifications.map((item) => (
              <article key={item.id} className="notification-item">
                <p>{item.message}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

export default DashboardPage;
