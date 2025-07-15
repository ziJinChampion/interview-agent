#!/usr/bin/env python3
"""
语音转文字使用示例
"""

import os
from app.core.voice_to_text import VoiceToTextService


def example_single_transcription():
    """单个文件转录示例"""
    print("=== 单个文件转录示例 ===")
    
    # 创建服务实例
    service = VoiceToTextService(
        default_service="whisper",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # 音频文件路径（请替换为实际的音频文件）
    audio_file = "example.wav"
    
    if os.path.exists(audio_file):
        try:
            # 使用本地 Whisper 转录
            result = service.transcribe_file(audio_file, service_type="whisper")
            print(f"转录结果: {result}")
            
            # 使用 OpenAI API 转录（如果有 API Key）
            if os.getenv("OPENAI_API_KEY"):
                result = service.transcribe_file(audio_file, service_type="openai")
                print(f"OpenAI 转录结果: {result}")
                
        except Exception as e:
            print(f"转录失败: {e}")
    else:
        print(f"音频文件不存在: {audio_file}")


def example_batch_transcription():
    """批量转录示例"""
    print("\n=== 批量转录示例 ===")
    
    # 创建服务实例
    service = VoiceToTextService(default_service="whisper")
    
    # 音频文件列表
    audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]
    
    # 检查文件是否存在
    existing_files = [f for f in audio_files if os.path.exists(f)]
    
    if existing_files:
        try:
            # 批量转录
            results = service.batch_transcribe(existing_files, service_type="whisper")
            
            print("批量转录结果:")
            for file, result in results.items():
                print(f"{file}: {result}")
                
        except Exception as e:
            print(f"批量转录失败: {e}")
    else:
        print("没有找到音频文件")


def example_audio_processing():
    """音频处理示例"""
    print("\n=== 音频处理示例 ===")
    
    from app.core.voice_to_text import AudioProcessor
    
    # 音频文件路径
    input_file = "input.mp3"
    output_file = "output.wav"
    
    if os.path.exists(input_file):
        try:
            # 转换音频格式
            AudioProcessor.convert_audio_format(input_file, output_file, "wav")
            print(f"音频格式转换完成: {input_file} -> {output_file}")
            
            # 加载音频
            audio_data, sample_rate = AudioProcessor.load_audio(output_file)
            print(f"音频加载成功: 采样率={sample_rate}Hz, 数据长度={len(audio_data)}")
            
        except Exception as e:
            print(f"音频处理失败: {e}")
    else:
        print(f"输入文件不存在: {input_file}")


def example_api_usage():
    """API 使用示例"""
    print("\n=== API 使用示例 ===")
    
    import requests
    
    # API 端点
    api_url = "http://localhost:8000/voice/transcribe"
    
    # 音频文件路径
    audio_file = "example.wav"
    
    if os.path.exists(audio_file):
        try:
            # 准备文件
            with open(audio_file, "rb") as f:
                files = {"file": f}
                data = {
                    "service_type": "whisper",
                    "language": "zh",
                    "task": "transcribe"
                }
                
                # 发送请求
                response = requests.post(api_url, files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"API 转录结果: {result}")
                else:
                    print(f"API 请求失败: {response.status_code}")
                    
        except Exception as e:
            print(f"API 调用失败: {e}")
    else:
        print(f"音频文件不存在: {audio_file}")


def main():
    """主函数"""
    print("语音转文字功能示例")
    print("=" * 50)
    
    # 运行各种示例
    example_single_transcription()
    example_batch_transcription()
    example_audio_processing()
    example_api_usage()
    
    print("\n" + "=" * 50)
    print("示例运行完成")


if __name__ == "__main__":
    main() 