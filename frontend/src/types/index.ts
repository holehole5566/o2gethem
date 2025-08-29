export interface User {
  id: number;
  username: string;
  email: string;
  hearts: number;
}

export interface CommentPost {
  id: number;
  user_id: number;
  target_gender: string;
  target_job: string;
  target_birth_year: number;
  target_height: number;
  target_app: string;
  comment: string;
  created_at: string;
  likes_count: number;
  user_liked: boolean;
  is_owner: boolean;
}

export interface DatingPost {
  id: number;
  user_id: number;
  title: string;
  description: string;
  target_gender: string;
  target_age_min: number;
  target_age_max: number;
  created_at: string;
  username: string;
  is_owner: boolean;
  already_messaged: boolean;
}