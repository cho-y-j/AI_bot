"""
로깅 유틸리티 모듈
"""
import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name, level='INFO', log_file=None, max_size=10*1024*1024, backup_count=5):
    """
    로거 설정 함수
    
    Args:
        name (str): 로거 이름
        level (str): 로깅 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): 로그 파일 경로 (None인 경우 콘솔만 출력)
        max_size (int): 로그 파일 최대 크기 (바이트)
        backup_count (int): 백업 파일 개수
        
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    # 로깅 레벨 설정
    level_dict = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    log_level = level_dict.get(level.upper(), logging.INFO)
    
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 기존 핸들러 제거
    if logger.handlers:
        logger.handlers.clear()
    
    # 포맷 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 추가 (지정된 경우)
    if log_file:
        # 로그 디렉토리 생성
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 파일 핸들러 설정
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_size, 
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger 