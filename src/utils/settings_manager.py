"""
설정 관리 및 암호화 모듈
"""
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SettingsManager:
    def __init__(self, settings_file="settings.json"):
        """
        설정 관리자 초기화
        
        Args:
            settings_file (str): 설정 파일 경로
        """
        self.settings_file = settings_file
        self.settings = {}
        self.encryption_key = None
        
        # 설정 파일 디렉토리 생성
        os.makedirs(os.path.dirname(os.path.abspath(settings_file)), exist_ok=True)
        
        # 기존 설정 로드
        self.load_settings()
    
    def generate_key(self, password):
        """
        비밀번호를 기반으로 암호화 키 생성
        
        Args:
            password (str): 사용자 비밀번호
        """
        salt = b'tradingbot_salt'  # 실제 운영 환경에서는 안전한 salt 사용 필요
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.encryption_key = Fernet(key)
    
    def encrypt_value(self, value):
        """
        값을 암호화
        
        Args:
            value (str): 암호화할 값
            
        Returns:
            str: 암호화된 값
        """
        if not self.encryption_key:
            raise ValueError("암호화 키가 설정되지 않았습니다. set_password()를 먼저 호출하세요.")
        
        return self.encryption_key.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value):
        """
        암호화된 값을 복호화
        
        Args:
            encrypted_value (str): 복호화할 값
            
        Returns:
            str: 복호화된 값
        """
        if not self.encryption_key:
            raise ValueError("암호화 키가 설정되지 않았습니다. set_password()를 먼저 호출하세요.")
        
        try:
            return self.encryption_key.decrypt(encrypted_value.encode()).decode()
        except Exception as e:
            raise ValueError(f"복호화 실패: {str(e)}")
    
    def set_password(self, password):
        """
        암호화에 사용할 비밀번호 설정
        
        Args:
            password (str): 사용자 비밀번호
        """
        self.generate_key(password)
    
    def save_settings(self):
        """설정을 파일에 저장"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4)
    
    def load_settings(self):
        """파일에서 설정을 로드"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {}
    
    def set(self, key, value, encrypt=False):
        """
        설정 값을 저장
        
        Args:
            key (str): 설정 키
            value (str): 설정 값
            encrypt (bool): 암호화 여부
        """
        if encrypt:
            value = self.encrypt_value(value)
        self.settings[key] = {"value": value, "encrypted": encrypt}
        self.save_settings()
    
    def get(self, key, default=None):
        """
        설정 값을 조회
        
        Args:
            key (str): 설정 키
            default: 기본 값
            
        Returns:
            설정 값 또는 기본 값
        """
        if key not in self.settings:
            return default
            
        data = self.settings[key]
        value = data["value"]
        
        if data.get("encrypted", False):
            try:
                value = self.decrypt_value(value)
            except ValueError:
                return default
                
        return value
    
    def remove(self, key):
        """
        설정 삭제
        
        Args:
            key (str): 삭제할 설정 키
        """
        if key in self.settings:
            del self.settings[key]
            self.save_settings()
    
    def clear(self):
        """모든 설정 삭제"""
        self.settings = {}
        self.save_settings() 