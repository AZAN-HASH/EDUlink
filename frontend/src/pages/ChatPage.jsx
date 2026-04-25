import { useEffect, useState } from "react";
import ChatWindow from "../components/ChatWindow";
import { chatService } from "../services/chatService";
import { socialService } from "../services/socialService";

function ChatPage() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [thread, setThread] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    socialService
      .getUsers()
      .then((response) => setUsers(response.data.data))
      .catch((loadError) => setError(loadError.response?.data?.message || "Failed to load users."));
  }, []);

  const openThread = async (user) => {
    setSelectedUser(user);
    try {
      const response = await chatService.getThread(user.id);
      setThread(response.data.data);
    } catch (loadError) {
      setError(loadError.response?.data?.message || "Failed to load conversation.");
    }
  };

  const sendMessage = async (body) => {
    if (!selectedUser) {
      return;
    }
    await chatService.sendMessage(selectedUser.id, { body });
    const response = await chatService.getThread(selectedUser.id);
    setThread(response.data.data);
  };

  return (
    <div className="two-column">
      <section className="panel">
        <div className="panel-header">
          <h3>Direct messages</h3>
        </div>
        {error ? <p className="error-text">{error}</p> : null}
        <div className="stack-sm">
          {users.map((user) => (
            <button key={user.id} className="list-row button-row" type="button" onClick={() => openThread(user)}>
              <div>
                <strong>{user.username}</strong>
                <p className="tiny-text">{user.location}</p>
              </div>
            </button>
          ))}
        </div>
      </section>
      <ChatWindow
        title={selectedUser ? `Chat with ${selectedUser.username}` : "Select a user"}
        messages={thread?.messages || []}
        onSend={sendMessage}
        disabled={!selectedUser}
        placeholder="Send a direct message"
      />
    </div>
  );
}

export default ChatPage;
