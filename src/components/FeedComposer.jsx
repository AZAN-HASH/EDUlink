import { useState } from "react";

function FeedComposer({ clubs = [], onSubmit, submitting }) {
  const [form, setForm] = useState({
    title: "",
    description: "",
    codeSnippet: "",
    clubId: ""
  });
  const [file, setFile] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const payload = new FormData();
    payload.append("title", form.title);
    payload.append("description", form.description);
    if (form.codeSnippet) {
      payload.append("code_snippet", form.codeSnippet);
    }
    if (form.clubId) {
      payload.append("club_id", form.clubId);
    }
    if (file) {
      payload.append("media", file);
    }

    await onSubmit(payload);
    setForm({ title: "", description: "", codeSnippet: "", clubId: "" });
    setFile(null);
  };

  return (
    <form className="panel composer-form" onSubmit={handleSubmit}>
      <div className="panel-header">
        <h3>Quick Post</h3>
        <span className="tiny-text">Share experiments, code, and club updates.</span>
      </div>
      <input
        className="input"
        placeholder="Project title"
        value={form.title}
        onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
        required
      />
      <textarea
        className="textarea"
        placeholder="What are you building or learning?"
        value={form.description}
        onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
        required
      />
      <textarea
        className="textarea code-area"
        placeholder="Optional code snippet"
        value={form.codeSnippet}
        onChange={(event) => setForm((current) => ({ ...current, codeSnippet: event.target.value }))}
      />
      <div className="inline-fields">
        <select
          className="input"
          value={form.clubId}
          onChange={(event) => setForm((current) => ({ ...current, clubId: event.target.value }))}
        >
          <option value="">Post to global feed</option>
          {clubs.map((club) => (
            <option key={club.id} value={club.id}>
              {club.name}
            </option>
          ))}
        </select>
        <input className="input" type="file" accept=".png,.jpg,.jpeg,.mp4" onChange={(event) => setFile(event.target.files?.[0] || null)} />
      </div>
      <button className="button-primary" type="submit" disabled={submitting}>
        {submitting ? "Publishing..." : "Publish Post"}
      </button>
    </form>
  );
}

export default FeedComposer;
