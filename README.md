# Home AI Assistant

一个基于Python开发的本地AI语音助手系统。

## 项目概述

本项目旨在创建一个运行在本地的AI语音助手，具有以下特点：
- 基于语音唤醒和交互
- 支持流式语音合成，实现快速响应
- 可扩展的工具集成能力
- 模块化设计，支持不同服务提供商

## 核心功能

1. **语音交互**
   - 语音唤醒（基于VAD+唤醒词的双重检测）
   - 语音识别（STT）
   - 语音合成（TTS）

2. **AI对话**
   - 支持流式对话
   - 工具调用能力
   - 上下文管理

3. **工具集成**
   - 基于Function Calling的工具调用
   - 可扩展的工具注册机制

## 技术架构

### 核心组件

1. **语音处理模块**
   - VAD（Voice Activity Detection）
   - 唤醒词检测（Porcupine）
   - STT服务（OpenAI Whisper API/Edge STT）
   - TTS服务（Edge TTS/OpenAI TTS）

2. **LLM模块**
   - 支持OpenAI兼容接口
   - 流式响应处理

3. **工具模块**
   - 工具注册中心
   - Function Calling Schema生成
   - 异步工具执行

### 关键流程

1. **语音唤醒流程**
   - VAD持续监听音频输入
   - 检测到语音活动时开始缓存音频
   - 使用Porcupine检查是否包含唤醒词
   - 触发助手激活

2. **对话流程**
   - 语音转文本
   - LLM处理并流式返回
   - 实时语音合成
   - 工具调用（如需要）

## 项目结构

```
home_ai/
├── config/
│   └── config.yaml          # 配置文件
├── src/
│   ├── main.py             # 主程序入口
│   ├── audio/              # 语音处理模块
│   │   ├── wake_word/      # 唤醒词检测
│   │   ├── tts/           # 语音合成
│   │   └── stt/           # 语音识别
│   ├── llm/               # LLM模块
│   ├── skills/            # 工具模块
│   └── core/              # 核心流程控制
├── tests/                 # 测试用例
└── docs/                 # 项目文档
```

## 依赖要求

主要依赖包：
- `webrtcvad`: VAD功能
- `pvporcupine`: 唤醒词检测
- `edge-tts`: 语音合成
- `openai`: AI对话
- `pyaudio`: 音频处理

详细依赖请参见 `requirements.txt`

## 开发计划

1. **Phase 1: 基础框架搭建**
   - 项目结构创建
   - 核心接口定义
   - 配置系统实现

2. **Phase 2: 语音模块实现**
   - VAD实现
   - 唤醒词检测
   - TTS流式处理
   - STT接入

3. **Phase 3: AI对话实现**
   - LLM接口实现
   - 对话流程管理
   - 工具调用框架

4. **Phase 4: 功能完善**
   - 基础工具集成
   - 错误处理完善
   - 性能优化

5. **Phase 5: 测试与文档**
   - 单元测试编写
   - 集成测试
   - 文档完善

## 配置说明

### API配置
请在 `config/config.yaml` 中配置相关API密钥和参数：
- Picovoice Access Key: 用于唤醒词检测
- OpenAI API Key: 用于语音识别、语音合成和对话功能（如果使用OpenAI相关服务）
- OpenAI API Base URL: 用于配置OpenAI兼容接口（可选）

### 语音服务配置

#### 语音合成（TTS）
支持以下引擎：
- Edge TTS：微软Edge的语音合成服务，免费使用
- OpenAI TTS：OpenAI的语音合成服务（需要API密钥）

配置示例：
```yaml
tts:
  type: "edge"  # 选择使用的引擎：edge 或 openai
  edge:
    voice: "zh-CN-XiaoxiaoNeural"
  openai:
    voice: "alloy"
    api_key: "${OPENAI_API_KEY}"
    api_base: "${OPENAI_API_BASE}"
```

#### 语音识别（STT）
支持以下引擎：
- Whisper API：OpenAI的语音识别服务（需要API密钥）
- Edge STT：微软Edge的语音识别服务

配置示例：
```yaml
stt:
  type: "whisper"  # 选择使用的引擎：whisper 或 edge
  whisper:
    model: "whisper-1"
    api_key: "${OPENAI_API_KEY}"
    api_base: "${OPENAI_API_BASE}"
  edge:
    language: "zh-CN"
```

### OpenAI兼容接口
本项目支持使用OpenAI兼容接口，可以通过配置`api_base`来使用不同的服务提供商：
1. 使用官方API：保持默认配置或设置为 `https://api.openai.com/v1`
2. 使用兼容接口：设置为您的API端点，如 `https://your-api-endpoint/v1`

支持兼容接口的功能：
- 语音识别（Whisper API）
- 语音合成（TTS API）
- 对话功能（Chat API）

## 使用说明

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置API密钥：
复制 `config/config.yaml.example` 到 `config/config.yaml` 并填写相关配置

3. 运行助手：
```bash
python src/main.py
```

## 许可证

[MIT License](LICENSE)
