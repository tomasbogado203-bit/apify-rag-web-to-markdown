# AI & RAG Clean Web to Markdown Extractor (LLM-Ready)

Convert any webpage, technical documentation, news article, or blog into clean, structured, and token-optimized Markdown. Designed specifically to feed **Large Language Models (GPT-4, Claude 3.5, Gemini, Llama 3)**, **Vector Databases (Pinecone, Chroma, Qdrant)**, and **RAG (Retrieval-Augmented Generation)** pipelines.

## 🚀 Features

- **Boilerplate & Noise Removal:** Strips navigation menus, footers, cookie banners, tracking scripts, and ads.
- **Token Estimation:** Calculates exact word counts and estimated LLM token usage for each document.
- **Hierarchical Headings:** Preserves `#`, `##`, `###` heading hierarchy for semantic chunking.
- **Code Block Preservation:** Keeps `<pre><code>` blocks formatted with syntax highlighting.
- **Batch Conversion:** Process single URLs or entire documentation sites in parallel.
- **Export Formats:** Direct export to **JSON**, **CSV**, **Excel**, or raw **Markdown (.md)** files.

## 📥 Input Example

```json
{
  "startUrls": [
    "https://docs.python.org/3/tutorial/index.html",
    "https://en.wikipedia.org/wiki/Large_language_model"
  ],
  "maxPages": 20,
  "includeImages": false,
  "includeLinks": true
}
```

## 📤 Output Format

Each record in the dataset includes:
- `url`: Source webpage URL
- `title`: Page title
- `headings`: List of major headings (H1-H3)
- `markdownContent`: Clean, formatted Markdown string
- `wordCount`: Total words
- `estimatedTokens`: Estimated OpenAI/Claude token count
- `statusCode`: HTTP status code
