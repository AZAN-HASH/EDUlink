import api from "./api";

export const authService = {
  login(payload) {
    return api.post("/login", payload);
  },
  register(payload) {
    return api.post("/register", payload);
  },
  logout() {
    return api.post("/logout");
  },
  getMe() {
    return api.get("/users/me");
  }
};
