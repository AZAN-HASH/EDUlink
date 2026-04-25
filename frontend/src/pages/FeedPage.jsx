import { startTransition, useEffect, useState } from "react";
import FeedComposer from "../components/FeedComposer";
import PostCard from "../components/PostCard";
import { useAuth } from "../context/AuthContext";
import { feedService } from "../services/feedService";
import { socialService } from "../services/socialService";

function FeedPage() {
  const { user } = useAuth();
  const [posts, setPosts] = useState([]);
  const [clubs, setClubs] = useState([]);
  const [sort, setSort] = useState("latest");
  const [feedType, setFeedType] = useState("global");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const loadFeed = async () => {
    try {
      const response = await feedService.getPosts({
        feed: feedType,
        sort,
        user_id: user?.id
      });
      setPosts(response.data.data);
    } catch (loadError) {
      setError(loadError.response?.data?.message || "Failed to load feed.");
    }
  };

  useEffect(() => {
    loadFeed();
  }, [sort, feedType, user?.id]);

  useEffect(() => {
    socialService.getClubs().then((response) => setClubs(response.data.data || []));
  }, []);

  const handleCreatePost = async (formData) => {
    setSubmitting(true);
    try {
      await feedService.createPost(formData);
      await loadFeed();
    } catch (submitError) {
      setError(submitError.response?.data?.message || "Failed to create post.");
    } finally {
      setSubmitting(false);
    }
  };

  const refreshAfterAction = async () => {
    await loadFeed();
  };

  const handleComment = async (postId, content) => {
    await feedService.commentOnPost(postId, { content });
    await refreshAfterAction();
  };

  const handleDelete = async (postId) => {
    await feedService.deletePost(postId);
    startTransition(() => setPosts((current) => current.filter((post) => post.id !== postId)));
  };

  return (
    <div className="stack-lg">
      <section className="panel top-controls">
        <div>
          <h3>Global science feed</h3>
          <p className="muted-text">Follow new builds, club updates, and experiment logs.</p>
        </div>
        <div className="inline-fields">
          <select className="input" value={feedType} onChange={(event) => setFeedType(event.target.value)}>
            <option value="global">Global</option>
            <option value="following">Following</option>
          </select>
          <select className="input" value={sort} onChange={(event) => setSort(event.target.value)}>
            <option value="latest">Latest</option>
            <option value="trending">Trending</option>
          </select>
        </div>
      </section>
      <FeedComposer clubs={clubs} onSubmit={handleCreatePost} submitting={submitting} />
      {error ? <p className="error-text">{error}</p> : null}
      <div className="stack-md">
        {posts.map((post) => (
          <PostCard
            key={post.id}
            post={post}
            canDelete={post.author_id === user?.id || user?.role === "admin"}
            onLike={(postId) => feedService.likePost(postId).then(refreshAfterAction)}
            onBookmark={(postId) => feedService.bookmarkPost(postId).then(refreshAfterAction)}
            onShare={(postId) => feedService.sharePost(postId).then(refreshAfterAction)}
            onComment={handleComment}
            onDelete={handleDelete}
          />
        ))}
      </div>
    </div>
  );
}

export default FeedPage;
