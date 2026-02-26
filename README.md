# Social Engagement Tool

Platform-agnostic social media engagement automation tool.

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

## Installation

```bash
cd social-engager
pip install -r requirements.txt
```

## Configuration

Copy `config/platforms.example.yaml` to `config/platforms.yaml` and add your credentials:

```yaml
instagram:
  username: "your_username"
  password: "your_password"
  # Or use session for more stability

engagement:
  daily_limit: 20  # Max comments per day
  min_delay: 30    # Seconds between actions
  max_delay: 120   # Random delay range
```

## Usage

```bash
# Run engagement for specific target
python main.py engage --platform instagram --hashtag rockclimbing --location "New York"

# Discover posts
python main.py discover --platform instagram --hashtag climbing

# Generate comments (no posting)
python main.py generate --post-url "https://..."
```

## Architecture

```
social-engager/
├── core/           # Platform-agnostic logic
├── adapters/      # Platform-specific implementations
├── config/        # Configuration
├── models/        # LLM wrapper
└── main.py        # CLI entry point
```

## Modules

### Core
- `engine.py` - Main orchestrator
- `discovery.py` - Post/user discovery
- `engagement.py` - Comment generation
- `analytics.py` - Results tracking

### Adapters
- `base.py` - Base adapter interface
- `instagram.py` - Instagram implementation
- `twitter.py` - Twitter (planned)

## Disclaimer

Use responsibly. This tool is for legitimate engagement with your target audience. Excessive automation may violate platform Terms of Service. The authors are not responsible for any account actions taken by platforms.

## License

MIT
