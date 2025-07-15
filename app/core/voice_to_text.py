#!/usr/bin/env python3
"""
语音转文字 (Speech-to-Text) 基本代码框架
支持多种语音识别服务和模型
"""

import os
import logging
import tempfile
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import wave
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioProcessor:
    """音频预处理工具类"""
    
    @staticmethod
    def load_audio(file_path: str) -> tuple:
        """加载音频文件"""
        try:
            with wave.open(file_path, 'rb') as wav_file:
                # 获取音频参数
                frames = wav_file.readframes(wav_file.getnframes())
                sample_rate = wav_file.getframerate()
                
                # 转换为numpy数组
                audio_data = np.frombuffer(frames, dtype=np.int16)
                return audio_data, sample_rate
        except Exception as e:
            logger.error(f"加载音频文件失败: {e}")
            raise
    
    @staticmethod
    def convert_audio_format(input_path: str, output_path: str, target_format: str = 'wav'):
        """转换音频格式"""
        try:
            import librosa
            import soundfile as sf
            
            # 加载音频
            audio, sr = librosa.load(input_path, sr=None)
            
            # 保存为指定格式
            sf.write(output_path, audio, sr)
            logger.info(f"音频格式转换完成: {input_path} -> {output_path}")
            
        except ImportError:
            logger.error("需要安装 librosa 和 soundfile 库")
            raise
        except Exception as e:
            logger.error(f"音频格式转换失败: {e}")
            raise


class SpeechToTextBase(ABC):
    """语音转文字基类"""
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        self.api_key = api_key
        self.config = config or {}
        self.setup()
    
    @abstractmethod
    def setup(self):
        """初始化设置"""
        pass
    
    @abstractmethod
    def transcribe(self, audio_path: str, **kwargs) -> str:
        """转录音频文件"""
        pass
    
    @abstractmethod
    def transcribe_stream(self, audio_stream, **kwargs) -> str:
        """转录音频流"""
        pass


class OpenAISpeechToText(SpeechToTextBase):
    """OpenAI Whisper API 实现"""
    
    def setup(self):
        """初始化 OpenAI 客户端"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI 客户端初始化成功")
        except ImportError:
            logger.error("需要安装 openai 库: pip install openai")
            raise
        except Exception as e:
            logger.error(f"OpenAI 客户端初始化失败: {e}")
            raise
    
    def transcribe(self, audio_path: str, **kwargs) -> str:
        """使用 OpenAI Whisper 转录音频"""
        try:
            with open(audio_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    **kwargs
                )
                return response.text
        except Exception as e:
            logger.error(f"OpenAI 转录失败: {e}")
            raise
    
    def transcribe_stream(self, audio_stream, **kwargs) -> str:
        """转录音频流"""
        try:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_stream,
                **kwargs
            )
            return response.text
        except Exception as e:
            logger.error(f"OpenAI 流转录失败: {e}")
            raise


class WhisperLocal(SpeechToTextBase):
    """本地 Whisper 模型实现"""
    
    def setup(self):
        """初始化本地 Whisper 模型"""
        try:
            import whisper
            self.model = whisper.load_model("base")  # 可选: tiny, base, small, medium, large
            logger.info("本地 Whisper 模型加载成功")
        except ImportError:
            logger.error("需要安装 whisper 库: pip install openai-whisper")
            raise
        except Exception as e:
            logger.error(f"本地 Whisper 模型加载失败: {e}")
            raise
    
    def transcribe(self, audio_path: str, **kwargs) -> str:
        """使用本地 Whisper 转录音频"""
        try:
            result = self.model.transcribe(audio_path, **kwargs)
            return result["text"]
        except Exception as e:
            logger.error(f"本地 Whisper 转录失败: {e}")
            raise
    
    def transcribe_stream(self, audio_stream, **kwargs) -> str:
        """转录音频流（需要先保存为临时文件）"""
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_stream)
                temp_path = temp_file.name
            
            try:
                result = self.model.transcribe(temp_path, **kwargs)
                return result["text"]
            finally:
                os.unlink(temp_path)  # 删除临时文件
        except Exception as e:
            logger.error(f"本地 Whisper 流转录失败: {e}")
            raise


class SpeechToTextFactory:
    """语音转文字工厂类"""
    
    @staticmethod
    def create(service_type: str, api_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> SpeechToTextBase:
        """创建语音转文字服务实例"""
        services = {
            "openai": OpenAISpeechToText,
            "whisper": WhisperLocal
        }
        
        if service_type not in services:
            raise ValueError(f"不支持的服务类型: {service_type}")
        
        return services[service_type](api_key, config)


class VoiceToTextService:
    """语音转文字服务管理器"""
    
    def __init__(self, default_service: str = "whisper", api_key: Optional[str] = None):
        self.default_service = default_service
        self.api_key = api_key
        self.services = {}
        self.audio_processor = AudioProcessor()
    
    def get_service(self, service_type: Optional[str] = None) -> SpeechToTextBase:
        """获取语音转文字服务"""
        service_type = service_type or self.default_service
        
        if service_type not in self.services:
            self.services[service_type] = SpeechToTextFactory.create(
                service_type, self.api_key
            )
        
        return self.services[service_type]
    
    def transcribe_file(self, audio_path: str, service_type: Optional[str] = None, **kwargs) -> str:
        """转录音频文件"""
        service = self.get_service(service_type)
        return service.transcribe(audio_path, **kwargs)
    
    def transcribe_stream(self, audio_stream, service_type: Optional[str] = None, **kwargs) -> str:
        """转录音频流"""
        service = self.get_service(service_type)
        return service.transcribe_stream(audio_stream, **kwargs)
    
    def batch_transcribe(self, audio_files: List[str], service_type: Optional[str] = None, **kwargs) -> Dict[str, str]:
        """批量转录音频文件"""
        results = {}
        service = self.get_service(service_type)
        
        for audio_file in audio_files:
            try:
                result = service.transcribe(audio_file, **kwargs)
                results[audio_file] = result
                logger.info(f"转录完成: {audio_file}")
            except Exception as e:
                logger.error(f"转录失败 {audio_file}: {e}")
                results[audio_file] = f"转录失败: {e}"
        
        return results


# 使用示例
def main():
    """主函数 - 使用示例"""
    
    # 配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 从环境变量获取
    AUDIO_FILE = "example.wav"  # 音频文件路径
    
    # 创建服务管理器
    service = VoiceToTextService(default_service="whisper", api_key=OPENAI_API_KEY)
    
    # 示例1: 使用本地 Whisper 转录
    try:
        if os.path.exists(AUDIO_FILE):
            result = service.transcribe_file(AUDIO_FILE, service_type="whisper")
            print(f"转录结果: {result}")
        else:
            print(f"音频文件不存在: {AUDIO_FILE}")
    except Exception as e:
        print(f"转录失败: {e}")
    
    # 示例2: 使用 OpenAI Whisper API 转录
    if OPENAI_API_KEY:
        try:
            result = service.transcribe_file(AUDIO_FILE, service_type="openai")
            print(f"OpenAI 转录结果: {result}")
        except Exception as e:
            print(f"OpenAI 转录失败: {e}")
    
    # 示例3: 批量转录
    audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]
    if all(os.path.exists(f) for f in audio_files):
        results = service.batch_transcribe(audio_files, service_type="whisper")
        for file, result in results.items():
            print(f"{file}: {result}")


if __name__ == "__main__":
    main()