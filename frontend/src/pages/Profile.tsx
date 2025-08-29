import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { getProfile } from "../services/api";
import { useApi } from "../hooks/useApi";
import type { User, CommentPost } from "../types";
import { MESSAGES } from "../constants";
import type { RootState } from "../store";

interface ProfileData {
  user_id: number;
  user: User;
  comment_posts: CommentPost[];
  dating_posts: any[];
}

export default function Profile() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const { isLoggedIn } = useSelector((state: RootState) => state.auth);
  const { execute, loading, error } = useApi();

  useEffect(() => {
    if (!isLoggedIn) {
      setProfile(null);
      return;
    }
    
    async function fetchProfile() {
      try {
        const data = await execute(() => getProfile());
        setProfile(data);
      } catch {
        // Error handled by useApi hook
      }
    }
    fetchProfile();
  }, [isLoggedIn]);

  if (!isLoggedIn) return (
    <div className="page-container">
      <h2>Profile</h2>
      <div className="message error">{MESSAGES.PLEASE_LOGIN}</div>
    </div>
  );

  if (loading) return (
    <div className="page-container">
      <h2>Profile</h2>
      <div>Loading...</div>
    </div>
  );

  if (error) return (
    <div className="page-container">
      <h2>Profile</h2>
      <div className="message error">{error}</div>
    </div>
  );

  return (
    <div className="page-container" style={{maxWidth: '800px'}}>
      <h2>Your Profile</h2>
      {profile && (
        <div>
          <div style={{background: 'white', padding: '2rem', borderRadius: '12px', marginBottom: '2rem', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'}}>
            <h3 style={{marginBottom: '1rem', color: '#667eea'}}>User Information</h3>
            <div style={{fontSize: '1rem', marginBottom: '0.5rem'}}><strong>Username:</strong> {profile.user.username}</div>
            <div style={{fontSize: '1rem', marginBottom: '0.5rem'}}><strong>Email:</strong> {profile.user.email}</div>
            <div style={{fontSize: '1rem', marginBottom: '0.5rem'}}><strong>User ID:</strong> {profile.user.id}</div>
            <div style={{fontSize: '1.2rem', color: '#e74c3c', fontWeight: 'bold'}}>
              ❤️ Hearts: {profile.user.hearts || 0}
            </div>
          </div>
          
          <div style={{background: 'white', padding: '2rem', borderRadius: '12px', marginBottom: '2rem', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'}}>
            <h3 style={{marginBottom: '1rem', color: '#667eea'}}>My Comment Posts ({profile.comment_posts.length})</h3>
            {profile.comment_posts.length > 0 ? (
              <div className="posts-grid">
                {profile.comment_posts.map((post) => (
                  <div key={post.id} className="post-card">
                    <div className="post-preview">
                      <div><strong>{post.target_gender}</strong> • {post.target_job}</div>
                      <div>{post.target_birth_year} • {post.target_height}cm</div>
                      <div style={{marginTop: '0.5rem', fontSize: '0.7rem'}}>{post.target_app}</div>
                      <div style={{marginTop: '0.5rem'}}>
                        <div className="comment-text" style={{fontSize: '0.75rem', color: '#888', marginBottom: '0.5rem'}}>
                          {post.comment.length > 50 ? post.comment.substring(0, 50) + '...' : post.comment}
                        </div>
                      </div>
                      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                        <span>❤️ {post.likes_count || 0}</span>
                        <span>{new Date(post.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{color: '#666', fontStyle: 'italic'}}>No comment posts yet.</p>
            )}
          </div>
          
          <div style={{background: 'white', padding: '2rem', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'}}>
            <h3 style={{marginBottom: '1rem', color: '#667eea'}}>My Dating Posts ({profile.dating_posts.length})</h3>
            {profile.dating_posts.length > 0 ? (
              <div className="posts-grid">
                {profile.dating_posts.map((post) => (
                  <div key={post.id} className="post-card">
                    <div className="post-preview">
                      <div><strong>{post.title}</strong></div>
                      <div style={{fontSize: '0.8rem', color: '#666', marginTop: '0.5rem'}}>
                        Looking for: {post.target_gender}, Age {post.target_age_min}-{post.target_age_max}
                      </div>
                      <div style={{fontSize: '0.75rem', color: '#888', marginTop: '0.5rem'}}>
                        {post.description.length > 50 ? post.description.substring(0, 50) + '...' : post.description}
                      </div>
                      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem'}}>
                        <span>💬 {post.message_count || 0}</span>
                        <span>{new Date(post.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{color: '#666', fontStyle: 'italic'}}>No dating posts yet.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
