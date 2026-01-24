import hashlib

class AuthService:
    def __init__(self, db):
        self.db = db

    def hash_pw(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        count = self.db.query("SELECT COUNT(*) FROM users").fetchone()[0]
        role = "admin" if count == 0 else "user"
        lvl = "EXECUTE" if count == 0 else "READ"
        try:
            self.db.query("INSERT INTO users (username, password, role, access_level) VALUES (?, ?, ?, ?)", 
                         (username, self.hash_pw(password), role, lvl))
            return True
        except: return False

    def login(self, username, password):
        return self.db.query("SELECT id, username, role, access_level FROM users WHERE username=? AND password=?", 
                            (username, self.hash_pw(password))).fetchone()
