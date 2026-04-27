import api from "./api";

export const chatService = {
  getThreads() {
    return api.get("/chats/threads");
  },
  getThread(userId) {
    return api.get(`/chats/threads/${userId}`);
  },
  sendMessage(userId, payload) {
    return api.post(`/chats/threads/${userId}/messages`, payload);
  },
  getClubMessages(clubId) {
    return api.get(`/chats/clubs/${clubId}/messages`);
  }
};
