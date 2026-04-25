import { NavLink, Outlet, useNavigate } from "react-router-dom";
import NotificationPanel from "./NotificationPanel";
import { useAuth } from "../context/AuthContext";
import { useSocket } from "../context/SocketContext";

function ShellLayout() {
  const { user, logout } = useAuth();
  const { notifications } = useSocket();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="brand-mark">EduLink</p>
          <h1>Science clubs, projects, and conversations in one place.</h1>
        </div>
        <nav className="nav-list">
          <NavLink to="/dashboard">Dashboard</NavLink>
          <NavLink to="/feed">Feed</NavLink>
          <NavLink to="/profile">Profile</NavLink>
          <NavLink to="/chat">Chat</NavLink>
          <NavLink to="/search">Search</NavLink>
          {user?.role === "admin" ? <NavLink to="/admin">Admin</NavLink> : null}
        </nav>
        <div className="sidebar-user">
          <p>{user?.username}</p>
          <span className="tiny-text">
            {user?.role} • {user?.location}
          </span>
          <button className="button-secondary" type="button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </aside>
      <main className="main-shell">
        <header className="topbar">
          <div>
            <p className="eyebrow">Connected learning network</p>
            <h2>Welcome back, {user?.username}</h2>
          </div>
          <button className="button-primary" type="button" onClick={() => navigate("/feed")}>
            Create Post
          </button>
        </header>
        <div className="content-grid">
          <section className="page-content">
            <Outlet />
          </section>
          <section className="side-content">
            <NotificationPanel items={notifications} />
          </section>
        </div>
      </main>
    </div>
  );
}

export default ShellLayout;
