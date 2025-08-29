import { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { getMessages, replyMessage, updateMessage } from "../services/api";
import type { RootState } from "../store";

export default function Mailbox() {
  const [messages, setMessages] = useState<any[]>([]);
  const [filteredMessages, setFilteredMessages] = useState<any[]>([]);
  const [selectedMessage, setSelectedMessage] = useState<any>(null);
  const [replyContent, setReplyContent] = useState("");
  const [editContent, setEditContent] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [msg, setMsg] = useState("");
  const [titleFilter, setTitleFilter] = useState("");
  const [recipientFilter, setRecipientFilter] = useState("");
  const { isLoggedIn } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    if (isLoggedIn) {
      fetchMessages();
    }
  }, [isLoggedIn]);

  useEffect(() => {
    applyFilters();
  }, [titleFilter, recipientFilter, messages]);

  const fetchMessages = async () => {
    try {
      const data = await getMessages();
      const msgs = data.messages || [];
      setMessages(msgs);
      setFilteredMessages(msgs);
    } catch (err) {
      console.log(err);
    }
  };

  const applyFilters = () => {
    let filtered = messages;
    
    if (titleFilter) {
      filtered = filtered.filter(msg => 
        msg.dating_post_title.toLowerCase().includes(titleFilter.toLowerCase())
      );
    }
    
    if (recipientFilter) {
      filtered = filtered.filter(msg => 
        msg.sender_username.toLowerCase().includes(recipientFilter.toLowerCase()) ||
        msg.receiver_username.toLowerCase().includes(recipientFilter.toLowerCase())
      );
    }
    
    setFilteredMessages(filtered);
  };

  const clearFilters = () => {
    setTitleFilter("");
    setRecipientFilter("");
    setFilteredMessages(messages);
  };

  const handleReply = async () => {
    if (!replyContent.trim()) return;
    
    try {
      await replyMessage(selectedMessage.id, replyContent);
      setMsg("Reply sent successfully!");
      setReplyContent("");
      fetchMessages();
      setSelectedMessage(null);
    } catch (err: any) {
      console.log(err);
      if (err.status === 400) {
        setMsg(err.message || "Cannot reply to this message");
      } else {
        setMsg("Failed to send reply");
      }
    }
  };

  const handleEdit = async () => {
    if (!editContent.trim()) return;
    
    try {
      await updateMessage(selectedMessage.id, editContent);
      setMsg("Message updated successfully!");
      setEditContent("");
      setIsEditing(false);
      fetchMessages();
      setSelectedMessage(null);
    } catch (err: any) {
      console.log(err);
      setMsg(err.message || "Failed to update message");
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="page-container">
        <h2>Mailbox</h2>
        <div className="message error">Please login</div>
      </div>
    );
  }

  return (
    <div className="page-container" style={{maxWidth: '100%', padding: '1rem'}}>
      <h2>Mailbox</h2>
      
      {msg && <div className="message success" style={{marginBottom: '1rem'}}>{msg}</div>}
      
      <div className="posts-layout">
        <div className="search-sidebar" style={{width: '350px', maxHeight: 'calc(100vh - 200px)', overflowY: 'auto'}}>
          <h3 style={{marginBottom: '1rem', fontSize: '1.1rem'}}>Messages</h3>
          
          <div className="search-form" style={{marginBottom: '1rem'}}>
            <input 
              placeholder="Filter by title"
              value={titleFilter}
              onChange={(e) => setTitleFilter(e.target.value)}
              style={{marginBottom: '0.5rem'}}
            />
            <input 
              placeholder="Filter by person"
              value={recipientFilter}
              onChange={(e) => setRecipientFilter(e.target.value)}
              style={{marginBottom: '0.5rem'}}
            />
            <div style={{display: 'flex', gap: '0.5rem'}}>
              <button onClick={applyFilters} style={{fontSize: '0.8rem', padding: '6px 12px'}}>Filter</button>
              <button onClick={clearFilters} style={{fontSize: '0.8rem', padding: '6px 12px', background: '#6c757d'}}>Clear</button>
            </div>
          </div>
          
          {filteredMessages.length > 0 ? (
            <div>
              {filteredMessages.map((message) => (
                <div 
                  key={message.id} 
                  className="post-card" 
                  onClick={() => setSelectedMessage(message)}
                  style={{
                    marginBottom: '0.5rem', 
                    cursor: 'pointer',
                    backgroundColor: selectedMessage?.id === message.id ? '#e8f4fd' : (message.sender_id ? '#fff3cd' : '#f8f9fa'),
                    border: selectedMessage?.id === message.id ? '2px solid #667eea' : (message.sender_id ? '2px solid #ffc107' : '2px solid transparent')
                  }}
                >
                  <div>
                    <div style={{fontWeight: 'bold', marginBottom: '0.3rem', fontSize: '0.9rem'}}>
                      Re: {message.dating_post_title}
                    </div>
                    <div style={{fontSize: '0.8rem', marginBottom: '0.3rem', color: '#666'}}>
                      {message.sender_id && <span style={{color: '#856404', fontWeight: 'bold'}}>📤 </span>}
                      {message.sender_username} → {message.receiver_username}
                    </div>
                    <div style={{fontSize: '0.75rem', color: '#888'}}>
                      {message.reply_to_message_id && (
                        <span style={{fontStyle: 'italic'}}>Reply to {message.original_sender_username} • </span>
                      )}
                      {message.content.length > 60 ? message.content.substring(0, 60) + '...' : message.content}
                    </div>
                    <div style={{fontSize: '0.7rem', color: '#999', marginTop: '0.3rem'}}>
                      {new Date(message.updated_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{color: '#666', fontStyle: 'italic', fontSize: '0.9rem'}}>
              {messages.length === 0 ? 'No messages yet.' : 'No messages match the filter.'}
            </p>
          )}
        </div>

        <div className="posts-main">
          {selectedMessage ? (
            <div>
              <div style={{marginBottom: '2rem'}}>
                <h3 style={{marginBottom: '1rem'}}>Re: {selectedMessage.dating_post_title}</h3>
                
                <div style={{fontSize: '0.9rem', marginBottom: '1rem', color: '#666'}}>
                  <strong>From:</strong> {selectedMessage.sender_username} → <strong>To:</strong> {selectedMessage.receiver_username}
                </div>
                
                {selectedMessage.reply_to_message_id && (
                  <div style={{marginBottom: '1.5rem'}}>
                    <div style={{fontWeight: 'bold', color: '#667eea', marginBottom: '0.5rem'}}>Replying to:</div>
                    <div className="comment-text" style={{background: '#f0f0f0', padding: '1rem', borderRadius: '8px', fontSize: '0.9rem'}}>
                      <div style={{fontSize: '0.8rem', color: '#666', marginBottom: '0.5rem'}}>From: {selectedMessage.original_sender_username}</div>
                      {selectedMessage.original_message_content}
                    </div>
                  </div>
                )}
                
                <div style={{marginBottom: '1.5rem'}}>
                  <div style={{fontWeight: 'bold', color: '#667eea', marginBottom: '0.5rem'}}>Message:</div>
                  <div className="comment-text" style={{background: '#f8f9fa', padding: '1.5rem', borderRadius: '8px', fontSize: '1rem'}}>
                    {selectedMessage.content}
                  </div>
                </div>
                
                <div style={{fontSize: '0.8rem', color: '#666', marginBottom: '2rem'}}>
                  Last updated: {new Date(selectedMessage.updated_at).toLocaleDateString()}
                </div>
              </div>
              
              <div className="post-actions" style={{borderTop: '1px solid #e1e5e9', paddingTop: '1.5rem'}}>
                {selectedMessage.receiver_id && !selectedMessage.already_replied ? (
                  <div style={{marginBottom: '1.5rem'}}>
                    <h4 style={{marginBottom: '0.5rem', color: '#667eea'}}>Reply:</h4>
                    <textarea 
                      placeholder="Write your reply..."
                      value={replyContent}
                      onChange={(e) => setReplyContent(e.target.value)}
                      rows={4}
                      style={{width: '100%', marginBottom: '1rem'}}
                    />
                    <button onClick={handleReply}>Send Reply</button>
                  </div>
                ) : selectedMessage.receiver_id && selectedMessage.already_replied ? (
                  <div style={{color: '#666', fontStyle: 'italic', marginBottom: '1.5rem', padding: '1rem', background: '#f8f9fa', borderRadius: '8px'}}>
                    You have already replied to this message
                  </div>
                ) : null}
                
                {selectedMessage.sender_id && (
                  <div>
                    {!isEditing ? (
                      <button onClick={() => {setIsEditing(true); setEditContent(selectedMessage.content);}} style={{background: '#6c757d'}}>
                        Edit Message
                      </button>
                    ) : (
                      <div>
                        <h4 style={{marginBottom: '0.5rem', color: '#667eea'}}>Edit Message:</h4>
                        <textarea 
                          value={editContent}
                          onChange={(e) => setEditContent(e.target.value)}
                          rows={4}
                          style={{width: '100%', marginBottom: '1rem'}}
                        />
                        <div style={{display: 'flex', gap: '1rem'}}>
                          <button onClick={handleEdit}>Update</button>
                          <button onClick={() => setIsEditing(false)} style={{background: '#6c757d'}}>Cancel</button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', color: '#666', fontStyle: 'italic'}}>
              Select a message to view details
            </div>
          )}
        </div>
      </div>


    </div>
  );
}