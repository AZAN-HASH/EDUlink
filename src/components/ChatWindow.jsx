import { useState } from "react";

function ChatWindow({ title, messages = [], onSend, disabled, placeholder = "Write a message" }) {
  const [body, setBody] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!body.trim()) {
      return;
    }
    await onSend(body);
    setBody("");
  };

  return (
    <section className="panel chat-panel">
      <div className="panel-header">
        <h3>{title}</h3>
      </div>
      <div className="chat-stream">
        {messages.length === 0 ? (
          <p className="muted-text">No messages yet.</p>
        ) : (
          messages.map((message) => (
            <article key={message.id} className="chat-bubble">
              <strong>{message.sender?.username || "Member"}</strong>
              <p>{message.body}</p>
              <span className="tiny-text">{new Date(message.created_at).toLocaleString()}</span>
            </article>
          ))
        )}
      </div>
      <form className="comment-form" onSubmit={handleSubmit}>
        <input
          className="input"
          placeholder={placeholder}
          value={body}
          onChange={(event) => setBody(event.target.value)}
          disabled={disabled}
        />
        <button className="button-primary" type="submit" disabled={disabled}>
          Send
        </button>
      </form>
    </section>
  );
}

export default ChatWindow;
