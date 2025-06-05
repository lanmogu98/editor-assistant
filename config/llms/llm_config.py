# Configuration
llm_config = {
    "API_BASE_URL": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    "MODELS": {
        "deepseek-r1": "deepseek-r1-250120",
        "deepseek-r1-latest": "deepseek-r1-250528",
        "deepseek-v3": "deepseek-v3-241226",
        "deepseek-v3-latest": "deepseek-v3-250324",
    },
    "TEMPERATURE": 0.6,
    "MAX_TOKENS": 4000,
    "PRICING": {
        "deepseek-r1": {
            "input": 4.00,  # RMB per 1M tokens
            "output": 16.00  # RMB per 1M tokens
        },
        "deepseek-v3": {
            "input": 2.00,  # RMB per 1M tokens
            "output": 8.00  # RMB per 1M tokens
        },
        "deepseek-r1-latest": {
            "input": 4.00,  # RMB per 1M tokens
            "output": 16.00  # RMB per 1M tokens
        },
        "deepseek-v3-latest": {
            "input": 2.00,  # RMB per 1M tokens
            "output": 8.00  # RMB per 1M tokens
        }
    }
}