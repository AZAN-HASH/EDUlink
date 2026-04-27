import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import ChatWindow from "../components/ChatWindow";
import { useAuth } from "../context/AuthContext";
import { useSocket } from "../context/SocketContext";
import { chatService } from "../services/chatService";
import { socialService } from "../services/socialService";

function ClubPage() {
  const { clubId } = useParams();
  const { user } = useAuth();
  const { socket } = useSocket();
  const [club, setClub] = useState(null);
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState("");

  const loadClub = async () => {
    try {
      const [clubResponse, messageResponse] = await Promise.all([
        socialService.getClub(clubId),
        chatService.getClubMessages(clubId)
      ]);
      setClub(clubResponse.data.data);
      setMessages(messageResponse.data.data);
    } catch (loadError) {
      setError(loadError.response?.data?.message || "Failed to load club.");
    }
  };

  useEffect(() => {
    loadClub();
  }, [clubId]);

  useEffect(() => {
    if (!socket) {
      return undefined;
    }
    socket.emit("join_club", { club_id: clubId });
    const listener = (message) => {
      if (Number(message.club_id) === Number(clubId)) {
        setMessages((current) => [...current, message]);
      }
    };
    socket.on("club_message", listener);
    return () => {
      socket.emit("leave_club", { club_id: clubId });
      socket.off("club_message", listener);
    };
  }, [socket, clubId]);

  const isLeader = club?.leader_id === user?.id || user?.role === "admin";

  const sendClubMessage = async (body) => {
    socket?.emit("club_message", { sender_id: user.id, club_id: clubId, body });
  };

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (!club) {
    return <div className="panel">Loading club...</div>;
  }

  return (
    <div className="stack-lg">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">{club.school?.name}</p>
          <h2>{club.name}</h2>
          <p>{club.description || "A place for members to share experiments, media, and code."}</p>
        </div>
        <div className="inline-fields">
          <button className="button-primary" type="button" onClick={() => socialService.joinClub(club.id)}>
            Join Club
          </button>
          <button className="button-secondary" type="button" onClick={() => socialService.leaveClub(club.id)}>
            Leave Club
          </button>
        </div>
      </section>

      <section className="two-column">
        <div className="panel">
          <div className="panel-header">
            <h3>Members</h3>
            <span className="tiny-text">{club.member_count} active members</span>
          </div>
          <div className="stack-sm">
            {club.members?.map((member) => (
              <article key={member.id} className="list-row">
                <div>
                  <strong>{member.user?.username}</strong>
                  <p className="tiny-text">
                    {member.role} • {member.status}
                  </p>
                </div>
                {isLeader && member.status === "pending" ? (
                  <button
                    className="button-ghost"
                    type="button"
                    onClick={() => socialService.approveMember(club.id, member.user.id).then(loadClub)}
                  >
                    Approve
                  </button>
                ) : null}
              </article>
            ))}
          </div>
        </div>
        <ChatWindow title="Club group chat" messages={messages} onSend={sendClubMessage} />
      </section>
    </div>
  );
}

export default ClubPage;
