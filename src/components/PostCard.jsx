import { useState } from "react";

function PostCard({ post, onLike, onBookmark, onShare, onComment, onDelete, canDelete }) {
  const [comment, setComment] = useState("");

  const submitComment = async (event) => {
    event.preventDefault();
    if (!comment.trim()) {
      return;
    }
    await onComment(post.id, comment);
    setComment("");
  };

  return (
    <article className="post-card">
      <div className="post-head">
        <div>
          <p className="eyebrow">{post.club?.name || "Global Feed"}</p>
          <h3>{post.title}</h3>
          <p className="tiny-text">
            by {post.author?.username || "Unknown"} • {new Date(post.created_at).toLocaleString()}
          </p>
        </div>
        {canDelete ? (
          <button className="button-ghost" type="button" onClick={() => onDelete(post.id)}>
            Delete
          </button>
        ) : null}
      </div>
      <p>{post.description}</p>
      {post.code_snippet ? <pre className="code-block">{post.code_snippet}</pre> : null}
      {post.media_filename ? (
        post.media_type === "image" ? (
          <img
            className="post-media"
            src={`${import.meta.env.VITE_API_URL || "http://localhost:5000"}/uploads/${post.media_filename}`}
            alt={post.title}
          />
        ) : (
          <video
            className="post-media"
            controls
            src={`${import.meta.env.VITE_API_URL || "http://localhost:5000"}/uploads/${post.media_filename}`}
          />
        )
      ) : null}
      <div className="post-actions">
        <button className="button-ghost" type="button" onClick={() => onLike(post.id)}>
          Like {post.likes_count}
        </button>
        <button className="button-ghost" type="button" onClick={() => onBookmark(post.id)}>
          Save
        </button>
        <button className="button-ghost" type="button" onClick={() => onShare(post.id)}>
          Share {post.shares_count}
        </button>
      </div>
      <form className="comment-form" onSubmit={submitComment}>
        <input
          className="input"
          placeholder="Add a comment"
          value={comment}
          onChange={(event) => setComment(event.target.value)}
        />
        <button className="button-primary" type="submit">
          Comment
        </button>
      </form>
      {post.comments?.length ? (
        <div className="comment-list">
          {post.comments.slice(0, 3).map((item) => (
            <div key={item.id} className="comment-row">
              <strong>{item.author?.username || "Member"}</strong>
              <span>{item.content}</span>
            </div>
          ))}
        </div>
      ) : null}
    </article>
  );
}

export default PostCard;
