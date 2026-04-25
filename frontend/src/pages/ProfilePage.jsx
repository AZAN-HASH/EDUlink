import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { socialService } from "../services/socialService";

function ProfilePage() {
  const { user, refreshProfile } = useAuth();
  const { userId } = useParams();
  const [profile, setProfile] = useState(null);
  const [form, setForm] = useState({ bio: "", school: "", location: "", profile_picture: "" });
  const [error, setError] = useState("");
  const isOwnProfile = !userId || Number(userId) === user?.id;

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = isOwnProfile ? await socialService.getUser(user.id) : await socialService.getUser(userId);
        const nextProfile = response.data.data;
        setProfile(nextProfile);
        setForm({
          bio: nextProfile.bio || "",
          school: nextProfile.school?.name || nextProfile.school_name || "",
          location: nextProfile.location || "",
          profile_picture: nextProfile.profile_picture || ""
        });
      } catch (loadError) {
        setError(loadError.response?.data?.message || "Failed to load profile.");
      }
    };

    if (user) {
      loadProfile();
    }
  }, [userId, user?.id]);

  const handleSave = async (event) => {
    event.preventDefault();
    try {
      const response = await socialService.updateUser(user.id, form);
      setProfile(response.data.data);
      await refreshProfile();
    } catch (saveError) {
      setError(saveError.response?.data?.message || "Failed to update profile.");
    }
  };

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (!profile) {
    return <div className="panel">Loading profile...</div>;
  }

  return (
    <div className="stack-lg">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">{profile.role}</p>
          <h2>{profile.username}</h2>
          <p>{profile.bio || "Add a short bio to explain what you love building."}</p>
        </div>
        <div className="stat-grid">
          <article>
            <span className="tiny-text">Followers</span>
            <strong>{profile.followers_count}</strong>
          </article>
          <article>
            <span className="tiny-text">Following</span>
            <strong>{profile.following_count}</strong>
          </article>
          <article>
            <span className="tiny-text">Projects</span>
            <strong>{profile.projects_posted}</strong>
          </article>
        </div>
      </section>

      <section className="two-column">
        <div className="panel">
          <h3>Profile details</h3>
          <div className="stack-sm">
            <p>
              <strong>Location:</strong> {profile.location}
            </p>
            <p>
              <strong>School:</strong> {profile.school?.name || profile.school_name || "Not set"}
            </p>
            <p>
              <strong>Joined clubs:</strong> {profile.joined_clubs.map((club) => club.name).join(", ") || "None yet"}
            </p>
          </div>
        </div>
        {isOwnProfile ? (
          <form className="panel stack-sm" onSubmit={handleSave}>
            <h3>Edit profile</h3>
            <textarea
              className="textarea"
              placeholder="Bio"
              value={form.bio}
              onChange={(event) => setForm((current) => ({ ...current, bio: event.target.value }))}
            />
            <input
              className="input"
              placeholder="School"
              value={form.school}
              onChange={(event) => setForm((current) => ({ ...current, school: event.target.value }))}
            />
            <input
              className="input"
              placeholder="Location"
              value={form.location}
              onChange={(event) => setForm((current) => ({ ...current, location: event.target.value }))}
            />
            <input
              className="input"
              placeholder="Profile picture URL"
              value={form.profile_picture}
              onChange={(event) => setForm((current) => ({ ...current, profile_picture: event.target.value }))}
            />
            <button className="button-primary" type="submit">
              Save Profile
            </button>
          </form>
        ) : (
          <div className="panel">
            <h3>Connect</h3>
            <button className="button-primary" type="button" onClick={() => socialService.followUser(profile.id)}>
              Follow user
            </button>
          </div>
        )}
      </section>
    </div>
  );
}

export default ProfilePage;
