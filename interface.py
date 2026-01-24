import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from datetime import datetime

class MainUI(QMainWindow):
    def __init__(self, auth_service, db, engine):
        super().__init__()
        self.auth = auth_service; self.db = db; self.engine = engine
        self.current_user = None
        self.setWindowTitle("SecureFile Pro")
        self.resize(1100, 800)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.init_auth_screens()

    def log_event(self, message):
        uid = self.current_user[0] if self.current_user else 0
        self.db.query("INSERT INTO logs (event, user_id) VALUES (?, ?)", (message, uid))

    def init_auth_screens(self):
        auth_style = """
            QMainWindow { background-color: #f5f6fa; }
            QFrame#Card { background-color: white; border-radius: 12px; border: 1px solid #dcdde1; }

            QLineEdit { padding: 12px; border: 1px solid #dcdde1; border-radius: 6px; background: white; }
            QPushButton#Primary { background-color: #2ecc71; color: white; font-weight: bold; border-radius: 6px; padding: 12px; }
        """
        self.setStyleSheet(auth_style)
        
        # LOGIN PAGE
        l_page = QWidget(); l_lay = QVBoxLayout(l_page); l_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card = QFrame(); card.setObjectName("Card"); card.setFixedWidth(380)
        c_lay = QVBoxLayout(card); c_lay.setContentsMargins(30,40,30,40); c_lay.setSpacing(15)
        self.u_in = QLineEdit(placeholderText="Username"); self.p_in = QLineEdit(placeholderText="Password", echoMode=QLineEdit.EchoMode.Password)
        l_btn = QPushButton("SIGN IN"); l_btn.setObjectName("Primary"); l_btn.clicked.connect(self.handle_login)
        reg_nav = QPushButton("Create Account"); reg_nav.setStyleSheet("border:none; color:#3498db;"); reg_nav.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        c_lay.addWidget(QLabel("<h1>Login</h1>", alignment=Qt.AlignmentFlag.AlignCenter)); c_lay.addWidget(self.u_in); c_lay.addWidget(self.p_in); c_lay.addWidget(l_btn); c_lay.addWidget(reg_nav)
        l_lay.addWidget(card); self.stack.addWidget(l_page)
        self.u_in.setStyleSheet("color: black;")
        self.p_in.setStyleSheet("color: black;")

        
        # REGISTER PAGE
        r_page = QWidget(); r_lay = QVBoxLayout(r_page); r_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rcard = QFrame(); rcard.setObjectName("Card"); rcard.setFixedWidth(380)
        rc_lay = QVBoxLayout(rcard); rc_lay.setContentsMargins(30,40,30,40); rc_lay.setSpacing(15)
        self.ru = QLineEdit(placeholderText="Username")
        self.rp = QLineEdit(placeholderText="Password", echoMode=QLineEdit.EchoMode.Password)
        self.rp2 = QLineEdit(placeholderText="Repeat Password", echoMode=QLineEdit.EchoMode.Password)
        rb = QPushButton("REGISTER"); rb.setObjectName("Primary"); rb.clicked.connect(self.handle_reg)
        back_btn = QPushButton("Back to Login"); back_btn.setStyleSheet("border:none; color:#3498db;"); back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        rc_lay.addWidget(QLabel("<h1>Register</h1>", alignment=Qt.AlignmentFlag.AlignCenter)); rc_lay.addWidget(self.ru); rc_lay.addWidget(self.rp); rc_lay.addWidget(self.rp2); rc_lay.addWidget(rb); rc_lay.addWidget(back_btn)
        r_lay.addWidget(rcard); self.stack.addWidget(r_page)
        self.ru.setStyleSheet("color: black;")
        self.rp.setStyleSheet("color: black;")
        self.rp2.setStyleSheet("color: black;")

    def handle_login(self):
        user = self.auth.login(self.u_in.text(), self.p_in.text())
        if user: 
            self.current_user = user; self.show_dashboard()
            self.log_event(f"User {user[1]} logged in.")
        else: QMessageBox.critical(self, "Error", "Invalid Login")

    def handle_reg(self):
        if not self.ru.text() or not self.rp.text(): return QMessageBox.warning(self, "Error", "Fields cannot be empty")
        if self.rp.text() != self.rp2.text(): return QMessageBox.warning(self, "Error", "Passwords do not match!")
        if self.auth.register(self.ru.text(), self.rp.text()): 
            QMessageBox.information(self, "Success", "Account Created!"); self.stack.setCurrentIndex(0)

    def show_dashboard(self):
        dash = QWidget(); hbox = QHBoxLayout(dash); hbox.setContentsMargins(0,0,0,0)
        sidebar = QFrame(); sidebar.setFixedWidth(220); sidebar.setStyleSheet("background-color: #2c3e50; color: white;")
        s_lay = QVBoxLayout(sidebar)
        self.nav = QListWidget()
        menu = ["🛡️ Monitoring"]
        if self.current_user[2] == 'admin': menu.extend(["📜 Logs", "📂 Backups", "🔔 Requests"])
        self.nav.addItems(menu); self.nav.currentRowChanged.connect(self.switch_sub)
        
        logout = QPushButton("Logout"); logout.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; margin: 10px;"); logout.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        s_lay.addWidget(QLabel("<h2>SECURE-FIM</h2>")); s_lay.addWidget(self.nav); s_lay.addStretch(); s_lay.addWidget(logout)
        
        self.sub_stack = QStackedWidget()
        self.sub_stack.addWidget(self.create_mon_ui())
        if self.current_user[2] == 'admin':
            self.sub_stack.addWidget(self.create_log_ui()); self.sub_stack.addWidget(self.create_bak_ui()); self.sub_stack.addWidget(self.create_req_ui())
            
        hbox.addWidget(sidebar); hbox.addWidget(self.sub_stack)
        self.stack.addWidget(dash); self.stack.setCurrentWidget(dash); self.refresh_folders()

    def create_mon_ui(self):
        pg = QWidget(); lay = QVBoxLayout(pg); lay.addWidget(QLabel("<h1>Folders</h1>"))
        f_bar = QHBoxLayout()
        if self.current_user[2] == 'admin':
            b1 = QPushButton("➕ Add Folder"); b1.clicked.connect(self.admin_add_folder)
            b2 = QPushButton("❌ Remove"); b2.clicked.connect(self.admin_remove_folder)
            b1.setStyleSheet("color: black;")
            b2.setStyleSheet("color: black;")

            f_bar.addWidget(b1); f_bar.addWidget(b2)
        else:
            b_req = QPushButton("📁 Request Monitoring")
            b_req.clicked.connect(self.user_request_folder)
            b_req.setStyleSheet("color: black;")

            b_perm = QPushButton("🔑 Request Upgrade")
            b_perm.clicked.connect(self.user_request_permission)
            b_perm.setStyleSheet("color: black;")

            f_bar.addWidget(b_req); f_bar.addWidget(b_perm)
        f_bar.addStretch(); lay.addLayout(f_bar)
        
        self.folder_list = QListWidget(); self.folder_list.setFixedHeight(150); self.folder_list.itemClicked.connect(self.refresh_files)
        lay.addWidget(self.folder_list); lay.addWidget(QLabel("<h1>Files</h1>"))
        i_bar = QHBoxLayout(); s_btn = QPushButton("🔍 Scan"); s_btn.clicked.connect(self.handle_scan); r_btn = QPushButton("⏪ Restore"); r_btn.clicked.connect(self.handle_restore)
        i_bar.addWidget(s_btn); i_bar.addWidget(r_btn); i_bar.addStretch(); lay.addLayout(i_bar)
        s_btn.setStyleSheet("color: black;")
        r_btn.setStyleSheet("color: black;")    

        self.f_table = QTableWidget(0, 2); self.f_table.setHorizontalHeaderLabels(["Name", "Status"])
        self.f_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lay.addWidget(self.f_table); return pg

    def handle_scan(self):
        if self.current_user[2] != 'admin' and self.current_user[3] == 'READ':
            return QMessageBox.warning(self, "Denied", "You need WRITE permission to scan.")
        curr = self.folder_list.currentItem()
        if not curr: return
        self.log_event(f"Scan started: {curr.text()}")
        for fid, path, oh in self.db.query("SELECT id, file_path, last_hash FROM watched_files WHERE folder_path=?", (curr.text(),)).fetchall():
            nh = self.engine.get_file_hash(path)
            if not nh: self.db.query("UPDATE watched_files SET status='DELETED' WHERE id=?", (fid,))
            elif nh != oh: 
                self.engine.backup_file(path, is_initial=False)
                self.db.query("UPDATE watched_files SET status='TAMPERED', last_hash=? WHERE id=?", (nh, fid))
                self.log_event(f"ALERT: Tamper detected at {path}")
        self.refresh_files()

    def handle_restore(self):
        if self.current_user[2] != 'admin' and self.current_user[3] != 'EXECUTE':
            return QMessageBox.warning(self, "Denied", "You need EXECUTE permission to restore.")
        row = self.f_table.currentRow()
        if row >= 0:
            path = self.f_table.item(row, 0).toolTip()
            ok, msg = self.engine.restore_file(path)
            if ok:
                new_h = self.engine.get_file_hash(path)
                self.db.query("UPDATE watched_files SET status='SECURE', last_hash=? WHERE file_path=?", (new_h, path))
                self.log_event(f"Restored: {path}"); self.refresh_files()
                QMessageBox.information(self, "Success", "File restored using Initial Safe Backup.")
            else:
                QMessageBox.critical(self, "Error", msg)

    def admin_add_folder(self):
        p = QFileDialog.getExistingDirectory(self, "Select Folder")
        if p:
            for path, h in self.engine.scan_directory(p):
                self.engine.backup_file(path, is_initial=True) 
                self.db.query("INSERT OR IGNORE INTO watched_files (file_path, folder_path, last_hash) VALUES (?,?,?)", (path, p, h))
            self.refresh_folders()

    def admin_remove_folder(self):
        curr = self.folder_list.currentItem()
        if curr:
            self.db.query("DELETE FROM watched_files WHERE folder_path=?", (curr.text(),))
            self.refresh_folders(); self.f_table.setRowCount(0)

    def user_request_folder(self):
        p = QFileDialog.getExistingDirectory(self, "Request Folder")
        if p: self.db.query("INSERT INTO access_requests (user_id, username, requested_level, folder_path) VALUES (?,?,?,?)", (self.current_user[0], self.current_user[1], "MONITOR", p))

    def user_request_permission(self):
        lvl, ok = QInputDialog.getItem(self, "Request Upgrade", "Level:", ["WRITE", "EXECUTE"], 0, False)
        if ok: self.db.query("INSERT INTO access_requests (user_id, username, requested_level, folder_path) VALUES (?,?,?,?)", (self.current_user[0], self.current_user[1], lvl, "PERM_UPGRADE"))

    def create_req_ui(self):
        pg = QWidget(); lay = QVBoxLayout(pg); lay.addWidget(QLabel("<h1>Admin Approvals</h1>"))
        self.req_t = QTableWidget(0, 3); self.req_t.setHorizontalHeaderLabels(["User", "Type", "Details"])
        self.req_t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        app = QPushButton("Approve"); app.clicked.connect(self.approve_req)
        lay.addWidget(self.req_t); lay.addWidget(app); return pg

    def approve_req(self):
        row = self.req_t.currentRow()
        if row < 0: return
        rid = self.req_t.item(row, 0).toolTip(); rtype = self.req_t.item(row,1).text(); detail = self.req_t.item(row,2).text(); uname = self.req_t.item(row,0).text()
        if rtype == "MONITOR":
            for p, h in self.engine.scan_directory(detail):
                self.engine.backup_file(p, is_initial=True)
                self.db.query("INSERT OR IGNORE INTO watched_files (file_path, folder_path, last_hash) VALUES (?,?,?)", (p, detail, h))
        else:
            self.db.query("UPDATE users SET access_level=? WHERE username=?", (rtype, uname))
        self.db.query("UPDATE access_requests SET status='APPROVED' WHERE id=?", (rid,))
        self.refresh_reqs(); self.refresh_folders()

    def refresh_reqs(self):
        self.req_t.setRowCount(0)
        for r, d in enumerate(self.db.query("SELECT id, username, requested_level, folder_path FROM access_requests WHERE status='PENDING'").fetchall()):
            self.req_t.insertRow(r)
            it = QTableWidgetItem(d[1]); it.setToolTip(str(d[0]))
            self.req_t.setItem(r, 0, it); self.req_t.setItem(r, 1, QTableWidgetItem(d[2])); self.req_t.setItem(r, 2, QTableWidgetItem(d[3]))

    def refresh_folders(self):
        self.folder_list.clear()
        for f in self.db.query("SELECT DISTINCT folder_path FROM watched_files").fetchall(): self.folder_list.addItem(f[0])

    def refresh_files(self):
        curr = self.folder_list.currentItem()
        if not curr: return
        self.f_table.setRowCount(0)
        for r, (p, s) in enumerate(self.db.query("SELECT file_path, status FROM watched_files WHERE folder_path=?", (curr.text(),)).fetchall()):
            self.f_table.insertRow(r)
            pi = QTableWidgetItem(os.path.basename(p)); pi.setToolTip(p); si = QTableWidgetItem(s)
            col = QColor("#2ecc71") if s == 'SECURE' else QColor("#e74c3c")
            pi.setForeground(QBrush(col)); self.f_table.setItem(r,0,pi); self.f_table.setItem(r,1,si)

    def create_log_ui(self):
        pg = QWidget(); lay = QVBoxLayout(pg); lay.addWidget(QLabel("<h1>Logs</h1>"))
        self.lt = QTableWidget(0, 2); self.lt.setHorizontalHeaderLabels(["Time", "Event"])
        self.lt.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); lay.addWidget(self.lt); return pg

    def refresh_logs(self):
        self.lt.setRowCount(0)
        for r, d in enumerate(self.db.query("SELECT timestamp, event FROM logs ORDER BY id DESC").fetchall()):
            self.lt.insertRow(r); self.lt.setItem(r, 0, QTableWidgetItem(str(d[0]))); self.lt.setItem(r, 1, QTableWidgetItem(str(d[1])))

    def create_bak_ui(self):
        pg = QWidget(); lay = QVBoxLayout(pg); lay.addWidget(QLabel("<h1>Backup History</h1>"))
        self.bl = QListWidget(); lay.addWidget(self.bl); return pg

    def refresh_backups(self):
        self.bl.clear()
        if os.path.exists("backups"):
            for root, dirs, files in os.walk("backups"):
                for f in files: self.bl.addItem(f)

    def switch_sub(self, i):
        self.sub_stack.setCurrentIndex(i)
        if self.current_user[2] == 'admin':
            if i == 1: self.refresh_logs()
            if i == 2: self.refresh_backups()
            if i == 3: self.refresh_reqs()
