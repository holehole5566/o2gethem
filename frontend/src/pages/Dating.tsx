import { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { useForm } from "react-hook-form";
import { createDatingPost, getDatingPosts, sendMessage, canPostDating } from "../services/api";
import type { RootState } from "../store";

interface DatingPostData {
  title: string;
  description: string;
  target_gender: string;
  target_age_min: number;
  target_age_max: number;
}

export default function Dating() {
  const [posts, setPosts] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [selectedPost, setSelectedPost] = useState<any>(null);
  const [messageContent, setMessageContent] = useState("");
  const [msg, setMsg] = useState("");
  const { isLoggedIn } = useSelector((state: RootState) => state.auth);
  const { register, handleSubmit, reset, formState: { errors } } = useForm<DatingPostData>();

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const data = await getDatingPosts();
      setPosts(data.posts || []);
    } catch (err) {
      console.log(err);
    }
  };

  const onSubmit = async (data: DatingPostData) => {
    try {
      await createDatingPost(data);
      setMsg("Dating post created successfully!");
      reset();
      setShowForm(false);
      fetchPosts();
    } catch (err: any) {
      console.log(err);
      if (err.status === 400) {
        setMsg(err.message || "Cannot create dating post");
      } else {
        setMsg("Failed to create dating post");
      }
    }
  };

  const handleCreatePostClick = async () => {
    if (showForm) {
      setShowForm(false);
      return;
    }
    
    try {
      const data = await canPostDating();
      if (data.can_post) {
        setShowForm(true);
      } else {
        setMsg("You can only post one dating post per day");
      }
    } catch (err) {
      console.log(err);
      setMsg("Failed to check posting status");
    }
  };

  const handleSendMessage = async () => {
    if (!messageContent.trim()) return;
    
    try {
      await sendMessage(selectedPost.id, messageContent);
      setMsg("Message sent successfully!");
      setMessageContent("");
      setSelectedPost(null);
    } catch (err: any) {
      console.log(err);
      if (err.status === 400) {
        setMsg(err.message || "Cannot send message");
      } else {
        setMsg("Failed to send message");
      }
    }
  };

  return (
    <div className="page-container" style={{maxWidth: '100%', padding: '1rem'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem'}}>
        <h2>Dating</h2>
        {isLoggedIn && (
          <button onClick={handleCreatePostClick}>
            {showForm ? 'Cancel' : 'Create Dating Post'}
          </button>
        )}
      </div>

      <div className="posts-layout">
        <div className="search-sidebar">
          <h3 style={{marginBottom: '1rem', fontSize: '1.1rem'}}>Filter</h3>
          <div className="search-form">
            <select>
              <option value="">Any Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </div>
          {msg && <div className="message success" style={{marginTop: '1rem', fontSize: '0.8rem'}}>{msg}</div>}
        </div>

        <div className="posts-main">
          <div className="posts-grid">
            {posts.map((post) => (
              <div key={post.id} className="post-card" onClick={() => setSelectedPost(post)}>
                <div className="post-preview">
                  <div><strong>{post.title}</strong></div>
                  <div style={{fontSize: '0.8rem', color: '#666', marginTop: '0.5rem'}}>
                    Looking for: {post.target_gender}, Age {post.target_age_min}-{post.target_age_max}
                  </div>
                  <div style={{fontSize: '0.75rem', color: '#888', marginTop: '0.5rem'}}>
                    {post.description.length > 80 ? post.description.substring(0, 80) + '...' : post.description}
                  </div>
                  <div style={{fontSize: '0.7rem', color: '#999', marginTop: '0.5rem'}}>
                    By {post.username} • {new Date(post.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {selectedPost && (
        <div className="modal" onClick={() => setSelectedPost(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>
              <h3>{selectedPost.title}</h3>
              <button onClick={() => setSelectedPost(null)} style={{background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer'}}>×</button>
            </div>
            
            <div style={{fontSize: '0.9rem', marginBottom: '0.5rem'}}>
              <strong>Looking for:</strong> {selectedPost.target_gender}, Age {selectedPost.target_age_min}-{selectedPost.target_age_max}
            </div>
            <div style={{fontSize: '0.8rem', color: '#666', marginBottom: '1rem'}}>
              By {selectedPost.username} • {new Date(selectedPost.created_at).toLocaleDateString()}
            </div>
            
            <div style={{marginBottom: '1rem'}}>
              <div style={{fontWeight: 'bold', color: '#667eea', marginBottom: '0.5rem'}}>Description:</div>
              <div className="comment-text">{selectedPost.description}</div>
            </div>
            
            {isLoggedIn && !selectedPost.is_owner && !selectedPost.already_messaged && (
              <div>
                <textarea 
                  placeholder="Write your message..."
                  value={messageContent}
                  onChange={(e) => setMessageContent(e.target.value)}
                  rows={3}
                  style={{width: '100%', marginBottom: '1rem'}}
                />
                <button onClick={handleSendMessage}>Send Message</button>
              </div>
            )}
            {isLoggedIn && selectedPost.is_owner && (
              <div style={{color: '#666', fontStyle: 'italic', textAlign: 'center', padding: '1rem'}}>
                This is your own post
              </div>
            )}
            {isLoggedIn && !selectedPost.is_owner && selectedPost.already_messaged && (
              <div style={{color: '#666', fontStyle: 'italic', textAlign: 'center', padding: '1rem'}}>
                You have already sent a message to this post
              </div>
            )}
          </div>
        </div>
      )}

      {showForm && (
        <div className="modal" onClick={() => setShowForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>
              <h3>Create Dating Post</h3>
              <button onClick={() => setShowForm(false)} style={{background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer'}}>×</button>
            </div>
            
            <form onSubmit={handleSubmit(onSubmit)} className="form">
              <input placeholder="Title" {...register("title", { required: "Title is required" })} />
              {errors.title && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.title.message}</span>}
              
              <textarea placeholder="Description" {...register("description", { required: "Description is required" })} rows={4} />
              {errors.description && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.description.message}</span>}
              
              <select {...register("target_gender", { required: "Target gender is required" })}>
                <option value="">Select Target Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
              {errors.target_gender && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.target_gender.message}</span>}
              
              <div style={{display: 'flex', gap: '1rem'}}>
                <input type="number" placeholder="Min Age" {...register("target_age_min", { required: "Min age is required", min: 18, max: 100 })} />
                <input type="number" placeholder="Max Age" {...register("target_age_max", { required: "Max age is required", min: 18, max: 100 })} />
              </div>
              {errors.target_age_min && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.target_age_min.message}</span>}
              {errors.target_age_max && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.target_age_max.message}</span>}
              
              <button type="submit">Create</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}