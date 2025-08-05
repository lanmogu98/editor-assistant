# User Customization Guide

## Overview

Editor Assistant keeps all user-editable configuration files outside the source code in `~/.editor_assistant/` to prevent accidental modifications to the system and ensure safe customization.

## Quick Start

```bash
# View your configuration
editor-assistant config show

# The first time you run this, it will automatically create:
# ~/.editor_assistant/user_prompts/           (customizable prompts)
# ~/.editor_assistant/user_llm_config.yml     (model configuration)
```

## Customizing Prompts

### Location and Structure

```text
~/.editor_assistant/
├── user_prompts/
│   ├── news_generator.txt      # Customize news article generation
│   ├── research_outliner.txt   # Customize research outline generation  
│   └── translator.txt          # Customize Chinese translation
└── user_llm_config.yml         # Model and provider configuration
```

### Why .txt Files?

Prompts are stored as `.txt` files instead of being embedded in Python code for several reasons:

1. **Easy Editing**: No programming knowledge required - just edit text
2. **Immediate Effect**: Changes apply instantly without restarting
3. **Version Control**: Track your prompt improvements in git
4. **Safe Customization**: No risk of breaking the source code
5. **Jinja2 Support**: Use variables and logic in prompts

### Editing Prompts

```bash
# Edit with your preferred editor
nano ~/.editor_assistant/user_prompts/news_generator.txt
code ~/.editor_assistant/user_prompts/research_outliner.txt
vim ~/.editor_assistant/user_prompts/translator.txt
```

### Prompt Template Features

Prompts support **Jinja2 templating** with variables:

```text
# In news_generator.txt
You are a science news writer for researcher audiences.

## Content to Process
{{ content }}

## Target Audience
Your readers are {{ audience_type | default("researchers") }}.

## Requirements
{% if word_count %}
- Write exactly {{ word_count }} words
{% else %}
- Write approximately 400 words
{% endif %}
```

**Available Variables:**
- `{{ content }}` - The source content to process
- `{{ title }}` - Document title (in translator.txt)
- Custom variables can be added by modifying the code

### Prompt Customization Examples

#### Example 1: Modify News Tone
```text
# Original: Professional tone
You are a professional science news editor...

# Modified: More engaging tone
You are an enthusiastic science communicator who makes research accessible and exciting...
```

#### Example 2: Add Special Instructions
```text
# Add to news_generator.txt
## Special Requirements
- Always include potential real-world applications
- Mention funding sources when available
- Add a "What's Next?" section for future research directions
```

#### Example 3: Customize Translation Style
```text
# In translator.txt - add specific terminology handling
## Translation Guidelines
- Preserve technical terms in English with Chinese explanations
- Use formal academic Chinese
- Include key English terms in parentheses: 机器学习 (machine learning)
```

## Adding Custom Models

### View Available Models

```bash
editor-assistant config models
```

### Add New Models

```bash
# OpenAI GPT-4 example
editor-assistant config add-model \
  --provider openai \
  --model-name gpt-4-turbo \
  --model-id gpt-4-0125-preview \
  --input-price 10.0 \
  --output-price 30.0 \
  --max-tokens 4000 \
  --context-window 128000

# Anthropic Claude example  
editor-assistant config add-model \
  --provider anthropic \
  --model-name claude-3-opus \
  --model-id claude-3-opus-20240229 \
  --input-price 15.0 \
  --output-price 75.0 \
  --max-tokens 4000 \
  --context-window 200000

# Local Ollama model example
editor-assistant config add-model \
  --provider ollama \
  --model-name llama3-70b \
  --model-id llama3:70b \
  --input-price 0.0 \
  --output-price 0.0 \
  --max-tokens 8000 \
  --context-window 32000
```

### Manual Model Configuration

Edit `~/.editor_assistant/user_llm_config.yml`:

```yaml
# Add new provider
my_custom_provider:
  api_key_env_var: "MY_API_KEY"
  api_base_url: "https://api.example.com/v1/chat/completions"
  temperature: 0.7
  max_tokens: 4000
  context_window: 100000
  models:
    my_model:
      id: "my-model-v1"
      pricing:
        input: 5.0    # Price per 1K input tokens in CNY
        output: 15.0  # Price per 1K output tokens in CNY

# Modify existing provider
deepseek:
  models:
    # Add new Deepseek model
    deepseek-experimental:
      id: "deepseek-experimental-model"
      pricing:
        input: 2.0
        output: 8.0
```

### Environment Variables for New Models

```bash
# Add API keys for custom providers
export MY_API_KEY="your_api_key_here"
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
```

## Advanced Customization

### Custom Prompt Variables

You can modify the source code to add custom variables to prompts:

```python
# In your prompt loading code
prompt = load_news_generator_prompt(
    content=content,
    audience_type="researchers",
    word_count=500,
    include_citations=True
)
```

### Backup Your Customizations

```bash
# Backup your configuration
cp -r ~/.editor_assistant/ ~/my_editor_assistant_backup/

# Version control your prompts
cd ~/.editor_assistant/
git init
git add .
git commit -m "Initial prompt customization"
```

### Share Configurations

```bash
# Share your prompts with others
tar -czf my_prompts.tar.gz -C ~ .editor_assistant/user_prompts/

# Or create a git repository
cd ~/.editor_assistant/user_prompts/
git remote add origin https://github.com/yourusername/my-editor-assistant-prompts.git
git push -u origin main
```

## Best Practices

### 1. Test Changes Incrementally
```bash
# Test with a small document first
editor-assistant news small_test.pdf --debug

# Check debug logs for any issues
tail -f logs/editor_assistant_*.log
```

### 2. Keep Backups
```bash
# Before major changes
cp ~/.editor_assistant/user_prompts/news_generator.txt \
   ~/.editor_assistant/user_prompts/news_generator.txt.backup
```

### 3. Use Version Control
```bash
cd ~/.editor_assistant/
git add user_prompts/
git commit -m "Improved news prompt for better methodology coverage"
```

### 4. Document Your Changes
```text
# Add comments to your prompts
## Modified 2024-01-15: Added emphasis on statistical significance
## Modified 2024-01-20: Improved technical terminology handling
```

## Troubleshooting

### Configuration Not Found
```bash
# Reinitialize configuration
editor-assistant config init
```

### Prompt Changes Not Working
```bash
# Check if you're editing the right file
editor-assistant config show

# Verify file permissions
ls -la ~/.editor_assistant/user_prompts/
```

### Model Not Available
```bash
# List available models
editor-assistant config models

# Check environment variables
echo $OPENAI_API_KEY
```

### Syntax Errors in YAML
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('~/.editor_assistant/user_llm_config.yml'))"
```

## Getting Help

1. **Configuration Issues**: `editor-assistant config show`
2. **Debug Mode**: Add `--debug` to any command
3. **Log Files**: Check `logs/editor_assistant_*.log`
4. **GitHub Issues**: Report bugs or request features

This system ensures you can fully customize Editor Assistant's behavior while keeping your modifications safe and separate from the source code!