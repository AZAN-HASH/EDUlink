import api from "./api";

export const socialService = {
  getDashboard() {
    return api.get("/dashboard");
  },
  getUsers() {
    return api.get("/users");
  },
  getUser(userId) {
    return api.get(`/users/${userId}`);
  },
  updateUser(userId, payload) {
    return api.put(`/users/${userId}`, payload);
  },
  followUser(userId) {
    return api.post(`/users/${userId}/follow`);
  },
  unfollowUser(userId) {
    return api.delete(`/users/${userId}/follow`);
  },
  getSchools() {
    return api.get("/schools");
  },
  createSchool(payload) {
    return api.post("/schools", payload);
  },
  joinSchool(schoolId) {
    return api.post(`/schools/${schoolId}/join`);
  },
  getClubs() {
    return api.get("/clubs");
  },
  getClub(clubId) {
    return api.get(`/clubs/${clubId}`);
  },
  createClub(payload) {
    return api.post("/clubs", payload);
  },
  joinClub(clubId) {
    return api.post(`/clubs/${clubId}/join`);
  },
  leaveClub(clubId) {
    return api.post(`/clubs/${clubId}/leave`);
  },
  approveMember(clubId, userId) {
    return api.post(`/clubs/${clubId}/members/${userId}/approve`);
  },
  getNotifications() {
    return api.get("/notifications");
  },
  readAllNotifications() {
    return api.post("/notifications/read-all");
  },
  getAdminOverview() {
    return api.get("/admin/overview");
  }
};
