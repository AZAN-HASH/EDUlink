import { startTransition, useDeferredValue, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { searchService } from "../services/searchService";

function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState({ users: [], schools: [], clubs: [], posts: [] });
  const [error, setError] = useState("");
  const deferredQuery = useDeferredValue(query);

  useEffect(() => {
    if (!deferredQuery.trim()) {
      setResults({ users: [], schools: [], clubs: [], posts: [] });
      return;
    }

    searchService
      .query(deferredQuery)
      .then((response) => {
        startTransition(() => setResults(response.data.data));
      })
      .catch((loadError) => setError(loadError.response?.data?.message || "Search failed."));
  }, [deferredQuery]);

  return (
    <div className="stack-lg">
      <section className="panel">
        <div className="panel-header">
          <h3>Search EduLink</h3>
        </div>
        <input
          className="input"
          placeholder="Search users, schools, clubs, or posts"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        {error ? <p className="error-text">{error}</p> : null}
      </section>

      <section className="search-grid">
        <div className="panel">
          <h3>Users</h3>
          {results.users.map((item) => (
            <Link key={item.id} className="list-row" to={`/profile/${item.id}`}>
              {item.username}
            </Link>
          ))}
        </div>
        <div className="panel">
          <h3>Schools</h3>
          {results.schools.map((item) => (
            <article key={item.id} className="list-row">
              {item.name}
            </article>
          ))}
        </div>
        <div className="panel">
          <h3>Clubs</h3>
          {results.clubs.map((item) => (
            <Link key={item.id} className="list-row" to={`/clubs/${item.id}`}>
              {item.name}
            </Link>
          ))}
        </div>
        <div className="panel">
          <h3>Posts</h3>
          {results.posts.map((item) => (
            <article key={item.id} className="list-row">
              <div>
                <strong>{item.title}</strong>
                <p className="tiny-text">{item.author?.username}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

export default SearchPage;
