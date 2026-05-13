# MysticForetell (神秘预言) - 占卜工程项目文档

## 1. 项目概述
MysticForetell 是一个集塔罗牌、易经、梅花易数于一体的占卜平台。本次优先实现了**塔罗牌占卜**的核心功能，并结合大语言模型（LLM）提供个性化的命运解读。

## 2. 技术栈
- **前端**: HTML5, Vanilla CSS3 (采用 Glassmorphism 玻璃拟态风格), Javascript (ES6 Modules)
- **后端**: FastAPI (Python), httpx
- **AI 模型**: 使用了 SiliconFlow 提供的 `GLM-Z1-9B-0414` 模型

## 3. 核心功能实现

### 塔罗规则 (Tarot Rules) - 专业级增强
- **全套 78 张牌**: 包含 22 张大阿卡纳与 56 张小阿卡纳（权杖、圣杯、宝剑、星币）。
- **真·洗牌逻辑**: 采用后端 Session 机制。洗牌后，牌阵中的每一张牌位置已固定，用户的点击即是真实的命运选择。
- **图像志数据**: 每张牌都包含详细的视觉图像描述（如“愚人脚下的悬崖”），辅助 AI 进行深度解读。
- **元素能量分析**: 自动分析牌阵中的风、火、水、土元素占比，提供全局能量平衡评估。

### 神秘感前端 (Mysterious UI)
- **仪式感交互**: 包含“心念汇聚（问题输入）”、“星辰洗牌”、“扇形点选”三个核心阶段。
- **动态选牌**: 78 张牌扇形平铺，支持悬浮预览与实时翻牌。
- **响应式设计**: 完美适配 PC 与 移动端。

### 个性化 AI 解读
- **宗师级 Prompt**: AI 结合图像学、元素平衡和用户问题进行多维度解析。
- **打字机效果**: 增强占卜结果呈现的神秘感。

## 4. 文件结构
```
MysticForetell/
├── index.html          # 前端主入口
├── server.py           # FastAPI 服务入口
├── config.py           # 配置文件 (API Key, 模型参数等)
├── engines/            # 核心引擎文件夹
│   ├── tarot.py        # 塔罗牌规则引擎
│   └── interpreter.py  # AI 解释引擎
├── css/
│   └── style.css       # 神秘学设计系统
├── js/
│   └── main.js         # 前端交互逻辑
└── assets/
    └── cards/
        └── back.png    # 卡牌背图
```

## 5. 启动指南
1. **安装依赖**:
   ```bash
   pip install fastapi uvicorn httpx
   ```
2. **配置 API Key**:
   在 `config.py` 中修改 `SILICONFLOW_API_KEY` 或设置环境变量。
3. **启动后端**:
   ```bash
   python3 server.py
   ```
4. **访问前端**:
   直接在浏览器打开 `index.html`。

---
**注意**: 占卜时请保持内心平静，默想你的问题。星辰会通过 AI 的低语给予你指引。
