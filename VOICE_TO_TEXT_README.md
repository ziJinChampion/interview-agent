# 语音转文字功能

这是一个集成了多种语音识别服务的语音转文字功能模块，支持本地和云端语音识别。

## 功能特性

- 🎯 **多种服务支持**: 支持 OpenAI Whisper API 和本地 Whisper 模型
- 📁 **批量处理**: 支持批量转录音频文件
- 🔄 **音频预处理**: 支持音频格式转换和预处理
- 🌐 **RESTful API**: 提供完整的 API 接口
- 🛡️ **错误处理**: 完善的错误处理和日志记录

## 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装音频处理相关依赖
pip install librosa soundfile openai-whisper pyaudio
```

## 快速开始

### 1. 基本使用

```python
from app.core.voice_to_text import VoiceToTextService

# 创建服务实例
service = VoiceToTextService(default_service="whisper")

# 转录音频文件
result = service.transcribe_file("audio.wav")
print(f"转录结果: {result}")
```

### 2. 使用 OpenAI API

```python
import os
from app.core.voice_to_text import VoiceToTextService

# 设置 API Key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# 创建服务实例
service = VoiceToTextService(default_service="openai", api_key=os.getenv("OPENAI_API_KEY"))

# 转录音频文件
result = service.transcribe_file("audio.wav", service_type="openai")
print(f"转录结果: {result}")
```

### 3. 批量转录

```python
from app.core.voice_to_text import VoiceToTextService

service = VoiceToTextService()

# 批量转录
audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]
results = service.batch_transcribe(audio_files)

for file, result in results.items():
    print(f"{file}: {result}")
```

## API 接口

### 1. 单个文件转录

**POST** `/voice/transcribe`

**参数:**
- `file`: 音频文件 (multipart/form-data)
- `service_type`: 服务类型 (whisper/openai)
- `language`: 语言代码 (zh/en)
- `task`: 任务类型 (transcribe/translate)

**示例:**
```bash
curl -X POST "http://localhost:8000/voice/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.wav" \
  -F "service_type=whisper" \
  -F "language=zh"
```

### 2. 批量转录

**POST** `/voice/transcribe-batch`

**参数:**
- `files`: 音频文件列表 (multipart/form-data)
- `service_type`: 服务类型

### 3. 获取可用服务

**GET** `/voice/services`

### 4. 健康检查

**GET** `/voice/health`

## 支持的服务

### 1. 本地 Whisper 模型

- **优点**: 无需网络连接，隐私性好
- **缺点**: 需要下载模型，占用本地资源
- **适用场景**: 离线环境，隐私要求高的场景

```python
service = VoiceToTextService(default_service="whisper")
result = service.transcribe_file("audio.wav", service_type="whisper")
```

### 2. OpenAI Whisper API

- **优点**: 准确度高，无需本地资源
- **缺点**: 需要网络连接，有 API 调用费用
- **适用场景**: 在线环境，对准确度要求高的场景

```python
service = VoiceToTextService(default_service="openai", api_key="your-api-key")
result = service.transcribe_file("audio.wav", service_type="openai")
```

## 音频格式支持

### 支持的输入格式
- WAV
- MP3
- M4A
- FLAC
- OGG
- 其他常见音频格式

### 音频要求
- **采样率**: 建议 16kHz 或以上
- **声道**: 单声道或立体声
- **时长**: 建议不超过 25MB (OpenAI API 限制)

## 音频预处理

```python
from app.core.voice_to_text import AudioProcessor

# 转换音频格式
AudioProcessor.convert_audio_format("input.mp3", "output.wav", "wav")

# 加载音频文件
audio_data, sample_rate = AudioProcessor.load_audio("audio.wav")
```

## 配置说明

### 环境变量

```bash
# OpenAI API Key
export OPENAI_API_KEY="your-api-key"

# 默认服务类型
export DEFAULT_VOICE_SERVICE="whisper"
```

### 服务配置

```python
# 创建服务时指定配置
config = {
    "model_size": "base",  # whisper 模型大小
    "language": "zh",      # 默认语言
    "task": "transcribe"   # 任务类型
}

service = VoiceToTextService(
    default_service="whisper",
    config=config
)
```

## 错误处理

```python
try:
    result = service.transcribe_file("audio.wav")
    print(f"转录成功: {result}")
except Exception as e:
    print(f"转录失败: {e}")
    # 处理错误
```

## 性能优化

### 1. 模型选择

```python
# 根据需求选择合适的模型大小
models = {
    "tiny": "最快，准确度较低",
    "base": "平衡速度和准确度",
    "small": "较好准确度",
    "medium": "高准确度",
    "large": "最高准确度，最慢"
}
```

### 2. 批量处理

```python
# 批量处理可以提高效率
audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]
results = service.batch_transcribe(audio_files)
```

### 3. 缓存机制

```python
# 服务实例会缓存模型，避免重复加载
service = VoiceToTextService()
# 第一次调用会加载模型
result1 = service.transcribe_file("audio1.wav")
# 第二次调用使用缓存的模型
result2 = service.transcribe_file("audio2.wav")
```

## 示例代码

完整的示例代码请参考 `voice_example.py` 文件。

## 故障排除

### 常见问题

1. **模型下载失败**
   ```bash
   # 手动下载模型
   python -c "import whisper; whisper.load_model('base')"
   ```

2. **音频格式不支持**
   ```python
   # 转换音频格式
   AudioProcessor.convert_audio_format("input.mp3", "output.wav")
   ```

3. **API 调用失败**
   ```python
   # 检查 API Key
   print(os.getenv("OPENAI_API_KEY"))
   ```

4. **内存不足**
   ```python
   # 使用较小的模型
   service = VoiceToTextService(config={"model_size": "tiny"})
   ```

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个功能。

## 许可证

本项目采用 MIT 许可证。 