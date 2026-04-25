import api from "./api";

export const feedService = {
  getPosts(params) {
    return api.get("/posts", { params });
  },
  createPost(formData) {
    return api.post("/posts", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });
  },
  likePost(postId) {
    return api.post(`/posts/${postId}/like`);
  },
  unlikePost(postId) {
    return api.delete(`/posts/${postId}/like`);
  },
  bookmarkPost(postId) {
    return api.post(`/posts/${postId}/bookmark`);
  },
  removeBookmark(postId) {
    return api.delete(`/posts/${postId}/bookmark`);
  },
  commentOnPost(postId, payload) {
    return api.post(`/posts/${postId}/comments`, payload);
  },
  sharePost(postId) {
    return api.post(`/posts/${postId}/share`);
  },
  deletePost(postId) {
    return api.delete(`/posts/${postId}`);
  }
};
