import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

class DatingService:
    def __init__(self, dsn: str):
        self.pool = psycopg2.pool.SimpleConnectionPool(1, 20, dsn, cursor_factory=RealDictCursor)
    
    def get_connection(self):
        return self.pool.getconn()
    
    def put_connection(self, conn):
        self.pool.putconn(conn)

    def create_dating_post(self, user_id: int, title: str, description: str, 
                          target_gender: str, target_age_min: int, target_age_max: int):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Check if user already posted today
                cur.execute(
                    """
                    SELECT id FROM dating_posts 
                    WHERE user_id = %s AND DATE(created_at) = CURRENT_DATE
                    """,
                    (user_id,)
                )
                if cur.fetchone():
                    raise ValueError("You can only post one dating post per day")
                
                cur.execute(
                    """
                    INSERT INTO dating_posts (user_id, title, description, target_gender, 
                                            target_age_min, target_age_max)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, user_id, title, description, target_gender, 
                             target_age_min, target_age_max, created_at
                    """,
                    (user_id, title, description, target_gender, target_age_min, target_age_max),
                )
                post = cur.fetchone()
                conn.commit()
                return post
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.put_connection(conn)

    def get_dating_posts(self, filters=None, user_id=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT dp.*, u.username,
                           CASE WHEN dp.user_id = %s THEN true ELSE false END as is_owner,
                           CASE WHEN EXISTS(
                               SELECT 1 FROM dating_messages dm 
                               WHERE dm.dating_post_id = dp.id AND dm.sender_id = %s AND dm.reply_to_message_id IS NULL
                           ) THEN true ELSE false END as already_messaged
                    FROM dating_posts dp
                    JOIN users u ON dp.user_id = u.id
                    WHERE 1=1
                """
                params = [user_id, user_id]
                
                if filters:
                    if filters.get('target_gender'):
                        query += " AND target_gender = %s"
                        params.append(filters['target_gender'])
                
                query += " ORDER BY dp.created_at DESC"
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            raise e
        finally:
            self.put_connection(conn)

    def send_message(self, sender_id: int, dating_post_id: int, content: str):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Get receiver_id from dating post
                cur.execute("SELECT user_id FROM dating_posts WHERE id = %s", (dating_post_id,))
                post = cur.fetchone()
                if not post:
                    raise ValueError("Dating post not found")
                
                receiver_id = post['user_id']
                if sender_id == receiver_id:
                    raise ValueError("Cannot send message to yourself")
                
                # Check if already sent message to this post (only initial messages, not replies)
                cur.execute(
                    "SELECT id FROM dating_messages WHERE sender_id = %s AND dating_post_id = %s AND reply_to_message_id IS NULL",
                    (sender_id, dating_post_id)
                )
                if cur.fetchone():
                    raise ValueError("Already sent message to this post")
                
                cur.execute(
                    """
                    INSERT INTO dating_messages (sender_id, receiver_id, dating_post_id, content)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, sender_id, receiver_id, dating_post_id, content, created_at, updated_at
                    """,
                    (sender_id, receiver_id, dating_post_id, content),
                )
                message = cur.fetchone()
                conn.commit()
                return message
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.put_connection(conn)

    def get_messages(self, user_id: int):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT dm.*, 
                           s.username as sender_username,
                           r.username as receiver_username,
                           dp.title as dating_post_title,
                           orig.content as original_message_content,
                           orig_sender.username as original_sender_username,
                           CASE WHEN dm.sender_id = %s THEN true ELSE false END as sender_id,
                           CASE WHEN dm.receiver_id = %s THEN true ELSE false END as receiver_id,
                           CASE WHEN EXISTS(
                               SELECT 1 FROM dating_messages reply 
                               WHERE reply.reply_to_message_id = dm.id AND reply.sender_id = %s
                           ) THEN true ELSE false END as already_replied
                    FROM dating_messages dm
                    JOIN users s ON dm.sender_id = s.id
                    JOIN users r ON dm.receiver_id = r.id
                    JOIN dating_posts dp ON dm.dating_post_id = dp.id
                    LEFT JOIN dating_messages orig ON dm.reply_to_message_id = orig.id
                    LEFT JOIN users orig_sender ON orig.sender_id = orig_sender.id
                    WHERE dm.sender_id = %s OR dm.receiver_id = %s
                    ORDER BY dm.created_at DESC
                    """,
                    (user_id, user_id, user_id, user_id, user_id)
                )
                return cur.fetchall()
        except Exception as e:
            raise e
        finally:
            self.put_connection(conn)

    def reply_message(self, message_id: int, user_id: int, reply_content: str):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Get original message
                cur.execute(
                    "SELECT * FROM dating_messages WHERE id = %s",
                    (message_id,)
                )
                original_message = cur.fetchone()
                if not original_message:
                    raise ValueError("Original message not found")
                
                # Check if user is receiver
                if original_message['receiver_id'] != user_id:
                    raise ValueError("Cannot reply to this message")
                
                # Check if already replied to this specific message
                cur.execute(
                    "SELECT id FROM dating_messages WHERE reply_to_message_id = %s AND sender_id = %s",
                    (message_id, user_id)
                )
                if cur.fetchone():
                    raise ValueError("Already replied to this message")
                
                # Create new message as reply
                cur.execute(
                    """
                    INSERT INTO dating_messages (sender_id, receiver_id, dating_post_id, content, reply_to_message_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (user_id, original_message['sender_id'], original_message['dating_post_id'], reply_content, message_id)
                )
                reply_message = cur.fetchone()
                conn.commit()
                return reply_message
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.put_connection(conn)

    def update_message(self, message_id: int, user_id: int, content: str):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE dating_messages 
                    SET content = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s AND sender_id = %s
                    RETURNING *
                    """,
                    (content, message_id, user_id)
                )
                message = cur.fetchone()
                if not message:
                    raise ValueError("Cannot update this message")
                conn.commit()
                return message
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.put_connection(conn)

    def can_post_today(self, user_id: int):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id FROM dating_posts 
                    WHERE user_id = %s AND DATE(created_at) = CURRENT_DATE
                    """,
                    (user_id,)
                )
                return cur.fetchone() is None
        except Exception as e:
            raise e
        finally:
            self.put_connection(conn)

    def get_user_dating_posts(self, user_id: int):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT dp.*, COUNT(dm.id) as message_count
                    FROM dating_posts dp
                    LEFT JOIN dating_messages dm ON dp.id = dm.dating_post_id AND dm.reply_to_message_id IS NULL
                    WHERE dp.user_id = %s
                    GROUP BY dp.id
                    ORDER BY dp.created_at DESC
                    """,
                    (user_id,)
                )
                return cur.fetchall()
        except Exception as e:
            raise e
        finally:
            self.put_connection(conn)

    def init_db(self):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dating_posts (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        title VARCHAR(200) NOT NULL,
                        description TEXT NOT NULL,
                        target_gender VARCHAR(10) NOT NULL,
                        target_age_min INTEGER NOT NULL,
                        target_age_max INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dating_messages (
                        id SERIAL PRIMARY KEY,
                        sender_id INTEGER REFERENCES users(id),
                        receiver_id INTEGER REFERENCES users(id),
                        dating_post_id INTEGER REFERENCES dating_posts(id),
                        content TEXT NOT NULL,
                        reply_to_message_id INTEGER REFERENCES dating_messages(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        finally:
            self.put_connection(conn)