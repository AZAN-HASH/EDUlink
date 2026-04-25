import api from "./api";

export const searchService = {
  query(term) {
    return api.get("/search", { params: { q: term } });
  }
};
