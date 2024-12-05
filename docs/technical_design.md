# 技术设计文档

## 1. 系统架构

### 1.1 整体架构
系统采用模块化设计，主要分为以下核心模块：
- 语音处理模块
- LLM对话模块
- 工具集成模块
- 核心控制模块

### 1.2 模块职责

#### 1.2.1 语音处理模块
负责所有与语音相关的处理，包括：
- 语音活动检测（VAD）
- 唤醒词识别
- 语音识别（STT）
- 语音合成（TTS）

#### 1.2.2 LLM对话模块
负责与语言模型的交互：
- 对话管理
- 流式响应处理
- 工具调用协调

#### 1.2.3 工具集成模块
提供系统扩展能力：
- 工具注册机制
- Function Calling适配
- 工具执行管理

#### 1.2.4 核心控制模块
协调各模块工作：
- 生命周期管理
- 错误处理
- 状态管理

## 2. 详细设计

### 2.1 语音唤醒设计

#### 2.1.1 双重检测机制
```
[音频输入] -> [VAD检测] -> [音频缓存] -> [唤醒词检测] -> [助手激活]
```

关键参数：
- VAD灵敏度：3（最高）
- 最小语音持续时间：250ms
- 语音填充时间：300ms
- 缓冲区最大长度：3秒

#### 2.1.2 状态管理
- 待机状态：仅运行VAD
- 检测状态：VAD+音频缓存
- 识别状态：唤醒词检测
- 激活状态：助手工作

### 2.2 语音合成设计

#### 2.2.1 基本架构
```
[文本输入] -> [TTS引擎] -> [音频数据] -> [音频播放]
     ↓           ↓            ↓           ↓
   句子级     异步转换     MP3格式     实时播放
```

#### 2.2.2 TTS引擎接口
```python
class BaseTTSEngine:
    async def text_to_speech(self, text: str) -> bytes:
        """将文本转换为音频数据"""
        pass
```

#### 2.2.3 优化策略
- 句子级处理：等待完整句子后再进行转换
- 异步转换：使用异步接口避免阻塞
- 音频缓存：缓存常用响应的音频数据
- 实时播放：使用pydub和sounddevice实现低延迟播放

#### 2.2.4 支持的引擎
1. Edge TTS
   - 优点：免费、低延迟、多语言支持
   - 配置：
     ```yaml
     tts:
       type: edge
       edge:
         voice: zh-CN-XiaoxiaoNeural
     ```

2. OpenAI TTS
   - 优点：高质量、自然度高
   - 配置：
     ```yaml
     tts:
       type: openai
       openai:
         api_key: your_api_key
         voice: alloy
         model: tts-1
     ```

### 2.3 工具集成框架

#### 2.3.1 注册机制
```python
@tool_registry.register
class TimeTool:
    name = "time"
    description = "Get current time"
    
    async def execute(self, **kwargs):
        return datetime.now().strftime("%H:%M:%S")
```

#### 2.3.2 Schema生成
自动生成符合OpenAI Function Calling格式的schema：
```json
{
    "name": "time",
    "description": "Get current time",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}
```

## 3. 接口定义

### 3.1 语音处理接口

#### 3.1.1 唤醒检测接口
```python
class BaseWakeWordDetector(ABC):
    @abstractmethod
    async def start_detection(self, callback: Callable[[], None]) -> None:
        pass

    @abstractmethod
    async def stop_detection(self) -> None:
        pass
```

#### 3.1.2 TTS接口
```python
class BaseTTSEngine(ABC):
    @abstractmethod
    async def text_to_speech_stream(
        self, 
        text_iterator: AsyncIterator[str]
    ) -> AsyncIterator[bytes]:
        pass
```

### 3.2 LLM接口
```python
class BaseLLM(ABC):
    @abstractmethod
    async def chat_stream(
        self, 
        messages: List[Dict[str, str]], 
        functions: List[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        pass
```

## 4. 配置规范

### 4.1 配置文件结构
```yaml
wake_word:
  porcupine:
    access_key: "${PICOVOICE_ACCESS_KEY}"
    keywords: ["hey computer"]
    sensitivities: [0.5]
  vad:
    aggressiveness: 3
    sample_rate: 16000
    frame_duration_ms: 30
    speech_pad_ms: 300
    min_speech_duration_ms: 250

tts:
  type: "edge"  # 选择使用的TTS引擎
  # Edge TTS配置
  edge:
    voice: "zh-CN-XiaoxiaoNeural"
  # OpenAI TTS配置
  openai:
    voice: "alloy"
    api_key: "${OPENAI_API_KEY}"
    api_base: "${OPENAI_API_BASE}"

stt:
  type: "whisper"  # 选择使用的STT引擎
  # Whisper API配置
  whisper:
    model: "whisper-1"
    api_key: "${OPENAI_API_KEY}"
    api_base: "${OPENAI_API_BASE}"
  # Edge STT配置
  edge:
    language: "zh-CN"

llm:
  type: "openai"
  model: "gpt-3.5-turbo"
  api_base: "${OPENAI_API_BASE}"
  temperature: 0.7
  max_tokens: 150
  api_key: "${OPENAI_API_KEY}"
```

### 4.2 组件配置说明

#### 4.2.1 TTS配置
- 通过`type`字段选择使用的TTS引擎
- 支持的引擎类型：
  - `edge`: Edge TTS
  - `openai`: OpenAI TTS
- 每种引擎的特定配置放在对应的配置块中

#### 4.2.2 STT配置
- 通过`type`字段选择使用的STT引擎
- 支持的引擎类型：
  - `whisper`: OpenAI Whisper API
  - `edge`: Edge STT
- 每种引擎的特定配置放在对应的配置块中

#### 4.2.3 扩展性
添加新的引擎支持只需：
1. 在配置中添加新的引擎类型
2. 添加对应的配置块
3. 实现相应的引擎接口

## 5. 错误处理

### 5.1 错误分类
- 配置错误
- 网络错误
- 服务错误
- 运行时错误

### 5.2 处理策略
1. 服务降级
2. 自动重试
3. 错误恢复
4. 用户反馈

## 6. 性能考虑

### 6.1 关键指标
- 唤醒响应时间：<500ms
- 语音合成延迟：<100ms
- 内存使用：<500MB

### 6.2 优化策略
1. 异步处理
2. 资源池化
3. 缓存机制
4. 并行处理

## 7. 扩展性设计

### 7.1 扩展点
1. 语音服务提供商
2. LLM模型
3. 工具集成
4. 配置项

### 7.2 插件机制
基于抽象基类和工厂模式实现插件化架构：
1. 定义接口
2. 实现适配器
3. 注册机制
4. 动态加载
