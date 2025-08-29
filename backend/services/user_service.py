import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, dsn: str):
        self.pool = psycopg2.pool.SimpleConnectionPool(1, 20, dsn, cursor_factory=RealDictCursor)
    
    def get_connection(self):
        return self.pool.getconn()
    
    def put_connection(self, conn):
        self.pool.putconn(conn)

    def create_user(self, username: str, email: str, password: str):
        hashed_pw = pwd_context.hash(password)
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (username, email, password_hash)
                    VALUES (%s, %s, %s)
                    RETURNING id, username, email
                    """,
                    (username, email, hashed_pw),
                )
                user = cur.fetchone()
                conn.commit()
                return user
        except psycopg2.IntegrityError as e:
            conn.rollback()
            if "username" in str(e):
                raise ValueError("Username already exists")
            elif "email" in str(e):
                raise ValueError("Email already exists")
            else:
                raise ValueError("User creation failed")
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.put_connection(conn)

    def authenticate_user(self, username: str, password: str):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, username, email, password_hash FROM users WHERE username = %s",
                    (username,),
                )
                user = cur.fetchone()
                if not user:
                    return None
                if not pwd_context.verify(password, user["password_hash"]):
                    return None
                return {"id": user["id"], "username": user["username"], "email": user["email"]}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.put_connection(conn)

    def get_user_by_id(self, user_id: int):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, username, email, hearts FROM users WHERE id = %s",
                    (user_id,),
                )
                return cur.fetchone()
        except Exception as e:
            raise e
        finally:
            self.put_connection(conn)

    def increment_hearts(self, user_id: int):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET hearts = hearts + 1 WHERE id = %s",
                    (user_id,)
                )
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.put_connection(conn)

    def init_db(self):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        hearts INTEGER DEFAULT 0
                    )
                """)
                conn.commit()
        finally:
            self.put_connection(conn)
