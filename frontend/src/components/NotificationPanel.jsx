function NotificationPanel({ items = [] }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h3>Notifications</h3>
      </div>
      {items.length === 0 ? (
        <p className="muted-text">You are all caught up.</p>
      ) : (
        <div className="stack-sm">
          {items.slice(0, 6).map((item) => (
            <article key={item.id} className={`notification-item ${item.is_read ? "" : "is-unread"}`}>
              <p>{item.message}</p>
              <span className="tiny-text">{new Date(item.created_at).toLocaleString()}</span>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default NotificationPanel;
