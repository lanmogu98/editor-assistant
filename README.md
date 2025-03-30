# Research Paper Summarizer

A tool for automatically summarizing research papers using LLMs. The system splits papers into manageable chunks, processes each chunk with an LLM, and then synthesizes the results into a comprehensive summary.

## Features

- Splits papers into chunks while preserving paragraph integrity
- Maintains context between chunks by passing summaries forward
- Generates structured summaries with key points, terminology, and figures
- Creates a final synthesis with executive summary and key takeaways
- Saves all prompts and responses for inspection

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file
   - Alternatively, you can set the `OPENAI_API_KEY` environment variable

## Usage

### Basic Usage

```bash
python paper_summarizer.py path/to/your/paper.md
```

This will:
1. Split the paper into chunks
2. Process each chunk with the LLM
3. Generate a final summary
4. Save all outputs to the `summaries` directory

### Command Line Options

```
usage: paper_summarizer.py [-h] [--output-dir OUTPUT_DIR] [--use-mock] [--api-key API_KEY] [--model MODEL] paper_path

Summarize research papers using LLM

positional arguments:
  paper_path            Path to the markdown file containing the paper

options:
  -h, --help            show this help mesdsage and exit
  --output-dir OUTPUT_DIR
                        Directory to save summaries (default: summaries)
  --api-key API_KEY     LLM API key (defaults to locally stored volc api key)
  --model MODEL         llm model to use (default: deepseek-R1)
```



## Output Structure

The summarizer creates the following directory structure for each paper:

```
summaries/
├── paper_name/
│   ├── prompts/
│   │   ├── chunk_1_prompt.txt
│   │   ├── chunk_2_prompt.txt
│   │   └── synthesis_prompt.txt
│   └── responses/
│       ├── chunk_1_response.md
│       ├── chunk_2_response.md
│       └── final_summary.md
└── paper_name_summary.md
```

- `prompts/`: Contains all prompts sent to the LLM
- `responses/`: Contains all responses from the LLM
- `paper_name_summary.md`: The final summary of the paper

## Customization

You can customize the system by:

1. Modifying the chunking parameters in `ContentChunker` initialization
2. Adjusting the prompt templates in `_create_chunk_analysis_prompt` and `_create_synthesis_prompt`
3. Changing the LLM model or parameters in the `OpenAIClient` class

## License

MIT 