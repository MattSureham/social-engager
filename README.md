# Social Engagement Tool

Platform-agnostic social media engagement automation tool with AI-powered comment generation.

## Features

- 🔍 **Discovery** - Find posts/users by hashtag, location, keywords
- 💬 **Smart Comments** - AI-generated contextual comments using LLM
- 🤖 **Automation** - Browser-based posting with human-like behavior
- 📊 **Analytics** - Track engagement results
- 🔌 **Plugin Architecture** - Easy to add new platforms

## Supported Platforms

| Platform | Status |
|----------|--------|
| Instagram | ✅ Ready |
| Twitter | 🔜 Coming soon |
| TikTok | 🔜 Coming soon |

## 环境要求

- Python 3.8+
- Playwright
- (可选) LLM API Key for smart comment generation

## 安装

```bash
# 克隆项目
git clone https://github.com/MattSureham/social-engager.git
cd social-engager

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

## 配置

### 1. 复制配置文件

```bash
cp config/platforms.example.yaml config/platforms.yaml
```

### 2. 配置 Instagram

编辑 `config/platforms.yaml`:

```yaml
instagram:
  username: "your_instagram_username"
  password: "your_instagram_password"
```

### 3. (可选) 配置 LLM 智能评论

如需 AI 生成评论，需要配置 LLM：

#### 方式一：使用环境变量

```bash
# MiniMax
export MINIMAX_API_KEY="your-minimax-key"

# 或 OpenAI
export OPENAI_API_KEY="your-openai-key"

# 或 Anthropic
export ANTHROPIC_API_KEY="your-anthropic-key"
```

#### 方式二：在配置文件中指定

```yaml
llm:
  provider: "minimax"  # minimax, openai, anthropic
  model: "MiniMax-M2.5"
```

### API Key 获取方式

| LLM | 获取地址 |
|-----|----------|
| MiniMax | https://platform.minimax.io |
| OpenAI | https://platform.openai.com |
| Anthropic | https://www.anthropic.com |

## 使用方法

### 1. 登录 Instagram

```bash
python main.py login --platform instagram
```

### 2. 发现帖子

```bash
# 按标签搜索
python main.py discover --hashtags rockclimbing

# 限制数量
python main.py discover --hashtags rockclimbing --limit 10

# 按位置筛选
python main.py discover --hashtags rockclimbing --location "New York"
```

### 3. 运行互动（自动评论）

```bash
# 基础用法
python main.py engage --hashtags rockclimbing

# 指定位置和每日限制
python main.py engage --hashtags rockclimbing --location "New York" --daily-limit 10

# 自定义评论风格
python main.py engage --hashtags rockclimbing --tone friendly
```

### 4. 查看统计

```bash
python main.py stats
```

## 命令行参数

### discover
```
--platform        平台 (默认 instagram)
--hashtags       标签，逗号分隔
--keywords       关键词，逗号分隔
--location       位置
--limit          结果数量限制
```

### engage
```
--platform        平台 (默认 instagram)
--hashtags       标签，逗号分隔 (必填)
--keywords       关键词，逗号分隔
--location       位置
--interests      目标受众兴趣
--tone           评论风格 (friendly, professional, casual, humorous)
--limit          处理帖子数量
--daily-limit    每日评论上限
--min-delay      每次操作最小间隔(秒)
--max-delay      每次操作最大间隔(秒)
```

### stats
```
--days            统计天数 (默认 7)
```

## 配置说明

完整配置选项 (`config/platforms.yaml`):

```yaml
# Instagram 配置
instagram:
  username: "your_username"
  password: "your_password"
  # 或使用 session 文件 (更稳定)
  session_file: ""
  # 代理 (可选)
  proxy: ""

# 互动设置
engagement:
  daily_limit: 20          # 每日最大互动数
  min_delay: 30            # 最小间隔(秒)
  max_delay: 120           # 最大间隔(秒)
  skip_engaged: true       # 跳过已互动帖子

# LLM 设置
llm:
  provider: "minimax"      # minimax, openai, anthropic
  model: "MiniMax-M2.5"
  temperature: 0.8

# 日志
logging:
  level: "INFO"
  file: "engagement.log"
```

## 架构

```
social-engager/
├── core/                    # 核心逻辑（平台无关）
│   ├── engine.py           # 主编排器
│   ├── discovery.py        # 发现模块
│   ├── engagement.py       # 互动模块
│   └── analytics.py        # 统计分析
│
├── adapters/               # 平台适配器
│   ├── base.py            # 基础接口
│   └── instagram.py       # Instagram 实现
│
├── config/                 # 配置文件
│   └── platforms.example.yaml
│
├── models/                 # 数据模型
└── main.py                # CLI 入口
```

## 添加新平台

要添加新平台（如 Twitter、TikTok），只需创建新的适配器：

```python
# adapters/twitter.py
from adapters.base import PlatformAdapter, Platform

class TwitterAdapter(PlatformAdapter):
    def get_platform(self) -> Platform:
        return Platform.TWITTER
    
    # 实现所有抽象方法...
```

## 注意事项

1. **风险提示**: 过度自动化可能违反平台服务条款，请谨慎使用
2. **建议**: 初始阶段使用较低的每日限制（如 10-20 条）
3. **安全**: 不要在配置文件中保存密码，考虑使用环境变量

## 常见问题

### Q: 登录失败怎么办？
A: 尝试使用 session 文件或降低操作频率

### Q: 没有 LLM key 怎么办？
A: 工具会使用模板生成评论，仍然可用

### Q: 被平台限制了怎么办？
A: 降低每日限制，增加操作间隔

## License

MIT
