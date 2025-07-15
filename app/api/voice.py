#!/usr/bin/env python3
"""
语音转文字 API 接口
"""

import os
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.voice_to_text import VoiceToTextService

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/voice", tags=["语音转文字"])

# 创建语音转文字服务实例
voice_service = VoiceToTextService(
    default_service="whisper",
    api_key=os.getenv("OPENAI_API_KEY")
)


class TranscriptionRequest(BaseModel):
    """转录请求模型"""
    service_type: Optional[str] = "whisper"
    language: Optional[str] = "zh"
    task: Optional[str] = "transcribe"


class TranscriptionResponse(BaseModel):
    """转录响应模型"""
    success: bool
    text: str
    service_type: str
    error: Optional[str] = None


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    service_type: str = Form("whisper"),
    language: str = Form("zh"),
    task: str = Form("transcribe")
):
    """
    转录音频文件
    
    Args:
        file: 上传的音频文件
        service_type: 服务类型 (whisper/openai)
        language: 语言代码
        task: 任务类型 (transcribe/translate)
    
    Returns:
        TranscriptionResponse: 转录结果
    """
    try:
        # 检查文件类型
        if not file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="只支持音频文件")
        
        # 保存临时文件
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # 执行转录
            result = voice_service.transcribe_file(
                temp_file_path,
                service_type=service_type,
                language=language,
                task=task
            )
            
            return TranscriptionResponse(
                success=True,
                text=result,
                service_type=service_type
            )
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        logger.error(f"转录失败: {e}")
        return TranscriptionResponse(
            success=False,
            text="",
            service_type=service_type,
            error=str(e)
        )


@router.post("/transcribe-batch")
async def batch_transcribe_audio(
    files: list[UploadFile] = File(...),
    service_type: str = Form("whisper")
):
    """
    批量转录音频文件
    
    Args:
        files: 上传的音频文件列表
        service_type: 服务类型
    
    Returns:
        Dict: 批量转录结果
    """
    try:
        results = {}
        temp_files = []
        
        try:
            # 保存所有临时文件
            for file in files:
                if not file.content_type.startswith("audio/"):
                    continue
                
                temp_file_path = f"/tmp/{file.filename}"
                with open(temp_file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                temp_files.append(temp_file_path)
            
            # 批量转录
            if temp_files:
                batch_results = voice_service.batch_transcribe(
                    temp_files,
                    service_type=service_type
                )
                
                # 将结果映射到原始文件名
                for temp_file, result in batch_results.items():
                    original_filename = os.path.basename(temp_file)
                    results[original_filename] = result
                    
        finally:
            # 清理临时文件
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        
        return {
            "success": True,
            "results": results,
            "service_type": service_type
        }
        
    except Exception as e:
        logger.error(f"批量转录失败: {e}")
        return {
            "success": False,
            "results": {},
            "error": str(e)
        }


@router.get("/services")
async def get_available_services():
    """
    获取可用的语音转文字服务
    
    Returns:
        Dict: 可用服务列表
    """
    return {
        "services": [
            {
                "name": "whisper",
                "description": "本地 Whisper 模型",
                "type": "local"
            },
            {
                "name": "openai",
                "description": "OpenAI Whisper API",
                "type": "cloud"
            }
        ]
    }


@router.get("/health")
async def health_check():
    """
    健康检查
    
    Returns:
        Dict: 服务状态
    """
    return {
        "status": "healthy",
        "service": "voice-to-text",
        "available_services": ["whisper", "openai"]
    } 