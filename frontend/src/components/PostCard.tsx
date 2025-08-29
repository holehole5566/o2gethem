import type{ CommentPost } from '../types';

interface PostCardProps {
  post: CommentPost;
  onClick: () => void;
}

export default function PostCard({ post, onClick }: PostCardProps) {
  return (
    <div className="post-card" onClick={onClick}>
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
  );
}