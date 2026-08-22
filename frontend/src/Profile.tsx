import { useState, useEffect, useRef, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import {
  getProfile,
  updateProfile,
  uploadAvatar,
  validateAvatarFile,
  resolveAvatarUrl,
  clearToken,
  ApiError,
  type Profile as ProfileType,
} from "./api";
import "./Profile.css";

type SaveStatus = "idle" | "saving" | "saved" | "error";

export default function Profile() {
  const [profile, setProfile] = useState<ProfileType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [displayName, setDisplayName] = useState("");
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");
  const [saveError, setSaveError] = useState<string | null>(null);

  const [avatarError, setAvatarError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [imageFailedToLoad, setImageFailedToLoad] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    setImageFailedToLoad(false);
  }, [profile?.avatar]);


  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const p = await getProfile();
        if (!cancelled) {
          setProfile(p);
          setDisplayName(p.display_name);
        }
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          navigate("/login", { replace: true });
          return;
        }
        if (!cancelled) {
          setError("Could not load profile. Please try again later.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [navigate]);

  async function handleSaveName(e: FormEvent) {
    e.preventDefault();
    if (!displayName.trim() || displayName === profile?.display_name) return;

    setSaveStatus("saving");
    setSaveError(null);

    try {
      const updated = await updateProfile(displayName.trim());
      setProfile(updated);
      setDisplayName(updated.display_name);
      setSaveStatus("saved");
      setTimeout(() => setSaveStatus("idle"), 2500);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        navigate("/login", { replace: true });
        return;
      }
      setSaveStatus("error");
      setSaveError("Could not save. Please try again.");
    }
  }

  async function handleAvatarChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setAvatarError(null);
    const validationError = validateAvatarFile(file);
    if (validationError) {
      setAvatarError(validationError);
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }

    setUploading(true);
    try {
      const updated = await uploadAvatar(file);
      setProfile(updated);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        navigate("/login", { replace: true });
        return;
      }
      if (err instanceof ApiError && err.body && typeof err.body === "object") {
        const bodyObj = err.body as Record<string, any>;
        const msg =
          Array.isArray(bodyObj.avatar) ? bodyObj.avatar[0] :
          typeof bodyObj.detail === "string" ? bodyObj.detail :
          typeof bodyObj.error === "string" ? bodyObj.error : null;
        if (msg) {
          setAvatarError(msg);
          return;
        }
      }
      setAvatarError("Upload failed. Please try again.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }


  function handleLogout() {
    clearToken();
    navigate("/login", { replace: true });
  }

  if (loading) {
    return (
      <div className="profile-page">
        <div className="profile-card" aria-busy="true">
          <div className="card-stamp">
            <span className="stamp-label">PROFILE</span>
            <span className="stamp-dash">&mdash;</span>
            <span className="stamp-label">ISSUED</span>
            <span className="stamp-date">&mdash;&mdash;&mdash;&mdash;</span>
          </div>
          <div className="card-body">
            <div className="photo-box photo-box--placeholder">
              <div className="loading-rule" />
            </div>
            <div className="card-fields">
              <div className="field-group">
                <span className="field-label">Full Name</span>
                <div className="loading-rule loading-rule--long" />
              </div>
              <div className="field-group">
                <span className="field-label">Email on File</span>
                <div className="loading-rule loading-rule--medium" />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-page">
        <div className="profile-card">
          <p className="card-error">{error}</p>
          <button className="btn btn--ink" onClick={() => window.location.reload()}>
            Try again
          </button>
        </div>
      </div>
    );
  }

  const issuedDate = profile
    ? new Date().toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      })
    : "";

  const resolvedAvatarUrl = resolveAvatarUrl(profile?.avatar);
  const showAvatarImage = Boolean(resolvedAvatarUrl) && !imageFailedToLoad;

  return (
    <div className="profile-page">
      <div className="profile-card">
        <div className="card-stamp">
          <span className="stamp-label">PROFILE</span>
          <span className="stamp-dash">&mdash;</span>
          <span className="stamp-label">ISSUED</span>
          <span className="stamp-date">{issuedDate}</span>
        </div>

        <div className="card-body">
          <div className="photo-box">
            {showAvatarImage ? (
              <img
                src={resolvedAvatarUrl!}
                alt={`Photo of ${profile?.display_name || "User"}`}
                className="photo-img"
                onError={() => setImageFailedToLoad(true)}
              />
            ) : (
              <div className="photo-placeholder">
                <span>No photo</span>
                <span>on file</span>
              </div>
            )}
          </div>


          <div className="card-fields">
            <form className="field-group" onSubmit={handleSaveName}>
              <label htmlFor="display-name" className="field-label">
                Full Name
              </label>
              <input
                id="display-name"
                type="text"
                className="field-input field-input--serif"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                disabled={saveStatus === "saving"}
              />
              <div className="field-actions">
                <button
                  type="submit"
                  className="btn btn--brass"
                  disabled={
                    saveStatus === "saving" ||
                    !displayName.trim() ||
                    displayName === profile?.display_name
                  }
                >
                  Save changes
                </button>
                {saveStatus === "saved" && (
                  <span className="inline-confirm">Saved</span>
                )}
                {saveStatus === "error" && saveError && (
                  <span className="inline-error">{saveError}</span>
                )}
              </div>
            </form>

            <div className="field-group">
              <span className="field-label">Email on File</span>
              <div className="field-readonly">{profile?.email}</div>
              <span className="field-note">Email cannot be changed</span>
            </div>
          </div>
        </div>

        <div className="card-footer">
          <div className="avatar-actions">
            <button
              className="btn btn--text"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? "Uploading..." : "Replace photo"}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="sr-only"
              onChange={handleAvatarChange}
            />
            {avatarError && <span className="inline-error">{avatarError}</span>}
          </div>

          <button className="btn btn--ghost" onClick={handleLogout}>
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}
