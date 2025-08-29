import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import PostCard from '../PostCard';
import type { CommentPost } from '../../types';

const mockPost: CommentPost = {
  id: 1,
  user_id: 1,
  target_gender: 'Female',
  target_job: 'Engineer',
  target_birth_year: 1995,
  target_height: 165,
  target_app: 'Tinder',
  comment: 'Test comment',
  created_at: '2024-01-01T00:00:00Z',
  likes_count: 5,
  user_liked: false,
  is_owner: false
};

describe('PostCard', () => {
  it('renders post information correctly', () => {
    const mockOnClick = vi.fn();
    
    render(<PostCard post={mockPost} onClick={mockOnClick} />);
    
    expect(screen.getByText(/Female/)).toBeInTheDocument();
    expect(screen.getByText(/Engineer/)).toBeInTheDocument();
    expect(screen.getByText(/1995/)).toBeInTheDocument();
    expect(screen.getByText(/165cm/)).toBeInTheDocument();
    expect(screen.getByText(/Tinder/)).toBeInTheDocument();
    expect(screen.getByText(/❤️ 5/)).toBeInTheDocument();
  });
  
  it('calls onClick when clicked', async () => {
    const user = userEvent.setup();
    const mockOnClick = vi.fn();
    
    const { container } = render(<PostCard post={mockPost} onClick={mockOnClick} />);
    
    const card = container.querySelector('.post-card') as HTMLElement;
    await user.click(card);
    
    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });
});