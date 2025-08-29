import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

class PostService:
    def __init__(self, dsn: str):
        self.pool = psycopg2.pool.SimpleConnectionPool(1, 20, dsn, cursor_factory=RealDictCursor)
    
    def get_connection(self):
        return self.pool.getconn()
    
    def put_connection(self, conn):
        self.pool.putconn(conn)

    def create_post(self, user_id: int, target_gender: str, target_job: str, 
                   target_birth_year: int, target_height: int, target_app: str, comment: str):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO comment_posts (user_id, target_gender, target_job, target_birth_year, 
                                     target_height, target_app, comment)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, user_id, target_gender, target_job, target_birth_year, 
                             target_height, target_app, comment, created_at
                    """,
                    (user_id, target_gender, target_job, target_birth_year, target_height, target_app, comment),
                )
                post = cur.fetchone()
                conn.commit()
                return post
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.put_connection(conn)

    def get_posts(self, filters=None, user_id=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT p.*, 
                           COUNT(pl.user_id) as likes_count,
                           CASE WHEN %s IS NOT NULL AND EXISTS(
                               SELECT 1 FROM comment_post_likes WHERE post_id = p.id AND user_id = %s
                           ) THEN true ELSE false END as user_liked,
                           CASE WHEN p.user_id = %s THEN true ELSE false END as is_owner
                    FROM comment_posts p
                    LEFT JOIN comment_post_likes pl ON p.id = pl.post_id
                    WHERE 1=1
                """
                params = [user_id, user_id, user_id]
                
                if filters:
                    if filters.get('target_gender'):
                        query += " AND target_gender = %s"
                        params.append(filters['target_gender'])
                    if filters.get('target_job'):
                        query += " AND target_job ILIKE %s"
                        params.append(f"%{filters['target_job']}%")
                    if filters.get('target_birth_year'):
                        query += " AND target_birth_year = %s"
                        params.append(filters['target_birth_year'])
                    if filters.get('height_min'):
                        query += " AND target_height >= %s"
                        params.append(filters['height_min'])
                    if filters.get('height_max'):
                        query += " AND target_height <= %s"
                        params.append(filters['height_max'])
                    if filters.get('target_app'):
                        query += " AND target_app ILIKE %s"
                        params.append(f"%{filters['target_app']}%")
                
                query += " GROUP BY p.id ORDER BY p.created_at DESC"
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            raise e
        finally:
            self.put_connection(conn)

    def update_post(self, post_id: int, user_id: int, target_gender: str, target_job: str,
                   target_birth_year: int, target_height: int, target_app: str, comment: str):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    UPDATE comment_posts SET target_gender=%s, target_job=%s, target_birth_year=%s,
                                   target_height=%s, target_app=%s, comment=%s
                    WHERE id=%s AND user_id=%s
                    RETURNING id, user_id, target_gender, target_job, target_birth_year,
                             target_height, target_app, comment, created_at
                    """,
                    (target_gender, target_job, target_birth_year, target_height, target_app, comment, post_id, user_id),
                )
                post = cur.fetchone()
                conn.commit()
                return post
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.put_connection(conn)

    def like_post(self, post_id: int, user_id: int):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Check if already liked
                cur.execute(
                    "SELECT 1 FROM comment_post_likes WHERE post_id = %s AND user_id = %s",
                    (post_id, user_id)
                )
                if cur.fetchone():
                    return False  # Already liked
                
                # Get post owner
                cur.execute("SELECT user_id FROM comment_posts WHERE id = %s", (post_id,))
                post = cur.fetchone()
                if not post:
                    return False
                
                # Insert like
                cur.execute(
                    "INSERT INTO comment_post_likes (post_id, user_id) VALUES (%s, %s)",
                    (post_id, user_id)
                )
                
                # Check if this user has ever given a heart to this post
                cur.execute(
                    "SELECT 1 FROM heart_history WHERE post_id = %s AND user_id = %s",
                    (post_id, user_id)
                )
                if not cur.fetchone():
                    # First time giving heart to this post, increment hearts and record it
                    cur.execute(
                        "INSERT INTO heart_history (post_id, user_id) VALUES (%s, %s)",
                        (post_id, user_id)
                    )
                    cur.execute(
                        "UPDATE users SET hearts = hearts + 1 WHERE id = %s",
                        (post['user_id'],)
                    )
                
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.put_connection(conn)

    def unlike_post(self, post_id: int, user_id: int):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM comment_post_likes WHERE post_id = %s AND user_id = %s",
                    (post_id, user_id)
                )
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.put_connection(conn)

    def get_user_posts(self, user_id: int):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT p.*, COUNT(pl.user_id) as likes_count
                    FROM comment_posts p
                    LEFT JOIN comment_post_likes pl ON p.id = pl.post_id
                    WHERE p.user_id = %s
                    GROUP BY p.id
                    ORDER BY p.created_at DESC
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
                    CREATE TABLE IF NOT EXISTS comment_posts (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        target_gender VARCHAR(10) NOT NULL,
                        target_job VARCHAR(100) NOT NULL,
                        target_birth_year INTEGER NOT NULL,
                        target_height INTEGER NOT NULL,
                        target_app VARCHAR(50) NOT NULL,
                        comment TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS comment_post_likes (
                        post_id INTEGER REFERENCES comment_posts(id) ON DELETE CASCADE,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (post_id, user_id)
                    )
                """)
                # Ensure unique constraint exists
                cur.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS unique_post_user_like 
                    ON comment_post_likes (post_id, user_id)
                """)
                # Create heart history table to track permanent heart awards
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS heart_history (
                        post_id INTEGER REFERENCES comment_posts(id) ON DELETE CASCADE,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (post_id, user_id)
                    )
                """)
                conn.commit()
        finally:
            self.put_connection(conn)