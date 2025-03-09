"""
환경 변수 로드 유틸리티 모듈
"""
import os
import logging
from dotenv import load_dotenv

from src.utils.logger import setup_logger

# 로거 설정
logger = setup_logger('env_loader')

def load_env_vars(env_file='.env'):
    """
    환경 변수 로드 함수
    
    Args:
        env_file (str): 환경 변수 파일 경로
        
    Returns:
        bool: 로드 성공 여부
    """
    # 환경 변수 파일 존재 확인
    if not os.path.exists(env_file):
        logger.warning(f"환경 변수 파일이 존재하지 않습니다: {env_file}")
        logger.info(f"{env_file}.example 파일을 복사하여 {env_file} 파일을 생성하세요.")
        return False
    
    # 환경 변수 로드
    load_dotenv(env_file)
    logger.info(f"환경 변수 로드 완료: {env_file}")
    
    # 필수 환경 변수 확인
    required_vars = [
        'KIWOOM_ACCOUNT',
        'OPENAI_API_KEY',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        return False
    
    return True

def get_env(key, default=None):
    """
    환경 변수 조회 함수
    
    Args:
        key (str): 환경 변수 키
        default: 기본값 (환경 변수가 없는 경우 반환)
        
    Returns:
        str: 환경 변수 값
    """
    value = os.getenv(key, default)
    if value is None:
        logger.warning(f"환경 변수가 설정되지 않았습니다: {key}")
    
    return value 