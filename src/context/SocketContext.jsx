import { createContext, useContext, useEffect, useState } from "react";
import { io } from "socket.io-client";
import { useAuth } from "./AuthContext";

const SocketContext = createContext(null);

export function SocketProvider({ children }) {
  const { user } = useAuth();
  const [socket, setSocket] = useState(null);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const accessToken = localStorage.getItem("edulink_access_token");
    if (!accessToken || !user) {
      if (socket) {
        socket.disconnect();
        setSocket(null);
      }
      return undefined;
    }

    const socketClient = io(import.meta.env.VITE_API_URL || "http://localhost:5000", {
      transports: ["websocket", "polling"]
    });

    socketClient.on("connect", () => {
      socketClient.emit("authenticate", { token: accessToken });
    });

    socketClient.on("notification", (notification) => {
      setNotifications((current) => [notification, ...current]);
    });

    setSocket(socketClient);
    return () => {
      socketClient.disconnect();
      setSocket(null);
    };
  }, [user?.id]);

  return <SocketContext.Provider value={{ socket, notifications }}>{children}</SocketContext.Provider>;
}

export function useSocket() {
  return useContext(SocketContext);
}
