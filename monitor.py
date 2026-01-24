import hashlib, os, shutil, glob
from datetime import datetime

class SecurityEngine:
    @staticmethod
    def get_file_hash(path):
        if not os.path.exists(path): return None
        sha256 = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                while chunk := f.read(4096): sha256.update(chunk)
            return sha256.hexdigest()
        except: return None

    @staticmethod
    def scan_directory(directory_path):
        results = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                full_path = os.path.join(root, file)
                file_hash = SecurityEngine.get_file_hash(full_path)
                if file_hash: results.append((full_path, file_hash))
        return results

    @staticmethod
    def backup_file(path, is_initial=False):
        safe_name = hashlib.md5(path.encode()).hexdigest()[:10]
        backup_dir = os.path.join("backups", safe_name)
        
        if not os.path.exists(backup_dir): 
            os.makedirs(backup_dir)
            
        prefix = "INITIAL_SAFE" if is_initial else "TAMPER_EVENT"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = os.path.join(backup_dir, f"{prefix}_{timestamp}_{os.path.basename(path)}")
        
        shutil.copy2(path, dest)
        return dest

    @staticmethod
    def restore_file(original_path):
        safe_name = hashlib.md5(original_path.encode()).hexdigest()[:10]
        backup_dir = os.path.join("backups", safe_name)
        
        if not os.path.exists(backup_dir): 
            return False, "No backup directory found for this file."
        
        
        backups = glob.glob(os.path.join(backup_dir, f"INITIAL_SAFE_*_{os.path.basename(original_path)}"))
        
        if not backups:
            return False, "No safe initial backup found."
        
    
        target_backup = min(backups, key=os.path.getctime)
        
        try:
            if os.path.exists(original_path):
                os.remove(original_path)
            shutil.copy2(target_backup, original_path)
            return True, "Restored successfully."
        except Exception as e:
            return False, f"Close the file first! Error: {str(e)}"