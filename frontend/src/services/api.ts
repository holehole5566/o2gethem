const API_BASE = import.meta.env.PROD ? '/api' : 'http://localhost:8000';

export async function register(username: string, email: string, password: string) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw { status: res.status, message: data.message || "Registration failed" };
  }
  return data;
}

export async function login(username: string, password: string) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw { status: res.status, message: data.message || "Login failed" };
  }
  return data;
}

export async function getProfile() {
  const res = await fetch(`${API_BASE}/users/profile`, {
    method: "GET",
    credentials: "include",
  });
  return res.json();
}

export async function logout() {
  const res = await fetch(`${API_BASE}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
  return res.json();
}

export async function createCommentPost(postData: any) {
  const res = await fetch(`${API_BASE}/comment_posts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(postData),
  });
  const data = await res.json();
  if (!res.ok) {
    throw { status: res.status, message: data.message || "Failed to create comment post" };
  }
  return data;
}

export async function getCommentPosts(filters?: any) {
  const params = new URLSearchParams(filters);
  const res = await fetch(`${API_BASE}/comment_posts?${params}`, {
    method: "GET",
    credentials: "include",
  });
  return res.json();
}

export async function updateCommentPost(postId: number, postData: any) {
  const res = await fetch(`${API_BASE}/comment_posts/${postId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(postData),
  });
  const data = await res.json();
  if (!res.ok) {
    throw { status: res.status, message: data.message || "Failed to update comment post" };
  }
  return data;
}

export async function likeCommentPost(postId: number) {
  const res = await fetch(`${API_BASE}/comment_posts/${postId}/like`, {
    method: "POST",
    credentials: "include",
  });
  const data = await res.json();
  if (!res.ok) {
    throw { status: res.status, message: data.message || "Failed to like comment post" };
  }
  return data;
}

export async function unlikeCommentPost(postId: number) {
  const res = await fetch(`${API_BASE}/comment_posts/${postId}/like`, {
    method: "DELETE",
    credentials: "include",
  });
  const data = await res.json();
  if (!res.ok) {
    throw { status: res.status, message: data.message || "Failed to unlike comment post" };
  }
  return data;
}

export async function createDatingPost(postData: any) {
  const res = await fetch(`${API_BASE}/dating`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(postData),
  });
  const data = await res.json();
  if (!res.ok) {
    throw { status: res.status, message: data.message || "Failed to create dating post" };
  }
  return data;
}

export async function getDatingPosts(filters?: any) {
  const params = new URLSearchParams(filters);
  const res = await fetch(`${API_BASE}/dating?${params}`, {
    method: "GET",
    credentials: "include",
  });
  return res.json();
}

export async function sendMessage(postId: number, content: string) {
  const res = await fetch(`${API_BASE}/dating/${postId}/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ content }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw { status: res.status, message: data.message || "Failed to send message" };
  }
  return data;
}

export async function getMessages() {
  const res = await fetch(`${API_BASE}/messages`, {
    method: "GET",
    credentials: "include",
  });
  return res.json();
}

export async function replyMessage(messageId: number, replyContent: string) {
  const res = await fetch(`${API_BASE}/messages/${messageId}/reply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ reply_content: replyContent }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw { status: res.status, message: data.message || "Failed to reply message" };
  }
  return data;
}

export async function updateMessage(messageId: number, content: string) {
  const res = await fetch(`${API_BASE}/messages/${messageId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ content }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw { status: res.status, message: data.message || "Failed to update message" };
  }
  return data;
}

export async function canPostDating() {
  const res = await fetch(`${API_BASE}/dating/can_post`, {
    method: "GET",
    credentials: "include",
  });
  return res.json();
}
