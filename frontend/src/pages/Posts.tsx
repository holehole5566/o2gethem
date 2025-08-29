import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { useForm } from "react-hook-form";
import { createCommentPost, getCommentPosts, updateCommentPost, likeCommentPost, unlikeCommentPost } from "../services/api";
import { useApi } from "../hooks/useApi";
import PostCard from "../components/PostCard";
import Modal from "../components/Modal";
import type { CommentPost } from "../types";
import { GENDER_OPTIONS, HEIGHT_RANGE, BIRTH_YEAR_RANGE, MESSAGES } from "../constants";
import type { RootState } from "../store";

interface PostFormData {
  target_gender: string;
  target_job: string;
  target_birth_year: number;
  target_height: number;
  target_app: string;
  comment: string;
}

export default function Posts() {
  const [posts, setPosts] = useState<CommentPost[]>([]);
  const [editingPost, setEditingPost] = useState<CommentPost | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [selectedPost, setSelectedPost] = useState<CommentPost | null>(null);
  const [msg, setMsg] = useState("");
  const { isLoggedIn } = useSelector((state: RootState) => state.auth);
  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm<PostFormData>();
  const { execute, loading, error } = useApi();

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const data = await execute(() => getCommentPosts());
      setPosts(data.posts || []);
    } catch (err) {
      console.log(err);
    }
  };

  const onSubmit = async (data: PostFormData) => {
    try {
      if (editingPost) {
        await execute(() => updateCommentPost(editingPost.id, data));
        setMsg(MESSAGES.POST_UPDATED);
      } else {
        await execute(() => createCommentPost(data));
        setMsg(MESSAGES.POST_CREATED);
      }
      reset();
      setEditingPost(null);
      setShowForm(false);
      fetchPosts();
    } catch (err: any) {
      console.log(err);
      setMsg("Failed to save post");
    }
  };

  const handleEdit = (post: CommentPost) => {
    setEditingPost(post);
    setValue("target_gender", post.target_gender);
    setValue("target_job", post.target_job);
    setValue("target_birth_year", post.target_birth_year);
    setValue("target_height", post.target_height);
    setValue("target_app", post.target_app);
    setValue("comment", post.comment);
    setSelectedPost(null);
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    const filters: any = {};
    
    formData.forEach((value, key) => {
      if (value) filters[key] = value;
    });

    try {
      const data = await getCommentPosts(filters);
      setPosts(data.posts || []);
    } catch (err) {
      console.log(err);
    }
  };

  const handleClearFilters = async () => {
    const form = document.querySelector('.search-form') as HTMLFormElement;
    form.reset();
    fetchPosts();
  };

  const handleLike = async (postId: number, isLiked: boolean) => {
    try {
      if (isLiked) {
        await unlikeCommentPost(postId);
      } else {
        await likeCommentPost(postId);
      }
      fetchPosts();
      if (selectedPost && selectedPost.id === postId) {
        setSelectedPost({...selectedPost, user_liked: !isLiked, likes_count: selectedPost.likes_count + (isLiked ? -1 : 1)});
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div className="page-container" style={{maxWidth: '100%', padding: '1rem'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem'}}>
        <h2>Posts</h2>
        {isLoggedIn && (
          <button onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : 'Create Post'}
          </button>
        )}
      </div>



      <div className="posts-layout">
        <div className="search-sidebar">
          <h3 style={{marginBottom: '1rem', fontSize: '1.1rem'}}>Search</h3>
          <form onSubmit={handleSearch} className="search-form">
            <select name="target_gender">
              {GENDER_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
            <input name="target_job" placeholder="Job" />
            <input name="target_birth_year" type="number" placeholder="Birth Year" min={BIRTH_YEAR_RANGE.MIN} max={BIRTH_YEAR_RANGE.MAX} />
            <div className="height-range">
              <span>Height:</span>
              <input name="height_min" type="number" placeholder="Min" min={HEIGHT_RANGE.MIN} max={HEIGHT_RANGE.MAX} />
              <span>-</span>
              <input name="height_max" type="number" placeholder="Max" min={HEIGHT_RANGE.MIN} max={HEIGHT_RANGE.MAX} />
              <span>cm</span>
            </div>
            <input name="target_app" placeholder="App" />
            <button type="submit">Search</button>
            <button type="button" onClick={handleClearFilters} style={{background: '#6c757d'}}>Clear</button>
          </form>
          {error && <div className="message error" style={{marginTop: '1rem', fontSize: '0.8rem'}}>{error}</div>}
          {msg && <div className="message success" style={{marginTop: '1rem', fontSize: '0.8rem'}}>{msg}</div>}
          {loading && <div style={{marginTop: '1rem', fontSize: '0.8rem', color: '#666'}}>Loading...</div>}
        </div>

        <div className="posts-main">
          <div className="posts-grid">
            {posts.map((post) => (
              <PostCard 
                key={post.id} 
                post={post} 
                onClick={() => setSelectedPost(post)} 
              />
            ))}
          </div>
        </div>
      </div>

      <Modal isOpen={!!selectedPost} onClose={() => setSelectedPost(null)} title="Post Details">
        {selectedPost && (
          <>
            <div style={{fontSize: '0.8rem', marginBottom: '0.5rem'}}><strong>Gender:</strong> {selectedPost.target_gender}</div>
            <div style={{fontSize: '0.8rem', marginBottom: '0.5rem'}}><strong>Job:</strong> {selectedPost.target_job}</div>
            <div style={{fontSize: '0.8rem', marginBottom: '0.5rem'}}><strong>Birth Year:</strong> {selectedPost.target_birth_year}</div>
            <div style={{fontSize: '0.8rem', marginBottom: '0.5rem'}}><strong>Height:</strong> {selectedPost.target_height}cm</div>
            <div style={{fontSize: '0.8rem', marginBottom: '1rem'}}><strong>App:</strong> {selectedPost.target_app}</div>
            <div style={{marginBottom: '1rem'}}>
              <div style={{fontWeight: 'bold', color: '#667eea', marginBottom: '0.5rem'}}>Comment:</div>
              <div className="comment-text">{selectedPost.comment}</div>
            </div>
            <div style={{fontSize: '0.8rem', color: '#666', marginBottom: '1rem'}}>Posted: {new Date(selectedPost.created_at).toLocaleDateString()}</div>
            
            <div className="post-actions">
              {isLoggedIn ? (
                <button 
                  onClick={() => handleLike(selectedPost.id, selectedPost.user_liked)}
                  style={{background: selectedPost.user_liked ? '#ff6b6b' : '#667eea'}}
                >
                  {selectedPost.user_liked ? '❤️' : '🤍'} {selectedPost.likes_count || 0}
                </button>
              ) : (
                <span>❤️ {selectedPost.likes_count || 0}</span>
              )}
              {isLoggedIn && selectedPost.is_owner && (
                <button onClick={() => handleEdit(selectedPost)}>Edit</button>
              )}
            </div>
          </>
        )}
      </Modal>

      <Modal isOpen={!!editingPost} onClose={() => setEditingPost(null)} title="Edit Post">
        {editingPost && (
          <form onSubmit={handleSubmit(onSubmit)} className="form">
              <select {...register("target_gender", { required: "Gender is required" })}>
                <option value="">Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
              {errors.target_gender && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.target_gender.message}</span>}
              
              <input placeholder="Target Job" {...register("target_job", { required: "Job is required" })} />
              {errors.target_job && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.target_job.message}</span>}
              
              <input type="number" placeholder="Birth Year" {...register("target_birth_year", { required: "Birth year is required", min: 1950, max: 2010 })} />
              {errors.target_birth_year && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.target_birth_year.message}</span>}
              
              <input type="number" placeholder="Height (cm)" {...register("target_height", { required: "Height is required", min: 140, max: 220 })} />
              {errors.target_height && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.target_height.message}</span>}
              
              <input placeholder="Target App" {...register("target_app", { required: "App is required" })} />
              {errors.target_app && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.target_app.message}</span>}
              
              <textarea placeholder="Comment" {...register("comment", { required: "Comment is required" })} rows={3} />
              {errors.comment && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.comment.message}</span>}
              
              <button type="submit">Update</button>
            </form>
        )}
      </Modal>

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="Create New Post">
        <form onSubmit={handleSubmit(onSubmit)} className="form">
              <select {...register("target_gender", { required: "Gender is required" })}>
                <option value="">Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
              {errors.target_gender && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.target_gender.message}</span>}
              
              <input placeholder="Target Job" {...register("target_job", { required: "Job is required" })} />
              {errors.target_job && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.target_job.message}</span>}
              
              <input type="number" placeholder="Birth Year" {...register("target_birth_year", { required: "Birth year is required", min: 1950, max: 2010 })} />
              {errors.target_birth_year && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.target_birth_year.message}</span>}
              
              <input type="number" placeholder="Height (cm)" {...register("target_height", { required: "Height is required", min: 140, max: 220 })} />
              {errors.target_height && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.target_height.message}</span>}
              
              <input placeholder="Target App" {...register("target_app", { required: "App is required" })} />
              {errors.target_app && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.target_app.message}</span>}
              
              <textarea placeholder="Comment" {...register("comment", { required: "Comment is required" })} rows={3} />
              {errors.comment && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.comment.message}</span>}
              
              <button type="submit">Create</button>
        </form>
      </Modal>
    </div>
  );
}