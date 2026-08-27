"""
AI & RAG Clean Web to Markdown Extractor Actor for Apify
Converts webpages and documentation into clean, token-optimized Markdown for LLMs.
"""

import asyncio
import re
import urllib.parse
from typing import Dict, Any, List
import httpx
from bs4 import BeautifulSoup
from apify import Actor

def html_to_clean_markdown(html_text: str, include_images: bool = False, include_links: bool = True) -> Dict[str, Any]:
    """Parses HTML and extracts structured, clean Markdown."""
    soup = BeautifulSoup(html_text, "html.parser")

    # Remove script, style, nav, footer, ads, cookie notices
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "form", "iframe"]):
        tag.decompose()

    # Extract title
    title = soup.title.get_text(strip=True) if soup.title else "Untitled Page"

    # Find main content container if available
    main_elem = soup.find("main") or soup.find("article") or soup.find("div", id=re.compile(r"content|main|article|body", re.I)) or soup.body or soup

    # Extract headings
    headings = [h.get_text(strip=True) for h in main_elem.find_all(["h1", "h2", "h3"]) if len(h.get_text(strip=True)) > 2]

    # Convert elements to markdown
    markdown_lines = []
    markdown_lines.append(f"# {title}\n")

    for elem in main_elem.find_all(["h1", "h2", "h3", "h4", "p", "ul", "ol", "pre", "blockquote"]):
        if elem.name == "h1":
            markdown_lines.append(f"\n# {elem.get_text(strip=True)}\n")
        elif elem.name == "h2":
            markdown_lines.append(f"\n## {elem.get_text(strip=True)}\n")
        elif elem.name == "h3":
            markdown_lines.append(f"\n### {elem.get_text(strip=True)}\n")
        elif elem.name == "h4":
            markdown_lines.append(f"\n#### {elem.get_text(strip=True)}\n")
        elif elem.name in ["ul", "ol"]:
            for li in elem.find_all("li", recursive=False):
                markdown_lines.append(f"- {li.get_text(strip=True)}")
            markdown_lines.append("")
        elif elem.name == "pre":
            code_text = elem.get_text()
            markdown_lines.append(f"\n```\n{code_text}\n```\n")
        elif elem.name == "blockquote":
            markdown_lines.append(f"> {elem.get_text(strip=True)}\n")
        elif elem.name == "p":
            text = elem.get_text(strip=True)
            if len(text) > 5:
                markdown_lines.append(f"{text}\n")

    full_markdown = "\n".join(markdown_lines).strip()
    
    # Calculate word count & estimated tokens (approx 1 token ~ 4 chars / 0.75 words)
    words = len(full_markdown.split())
    estimated_tokens = int(words * 1.33)

    return {
        "title": title,
        "headings": headings[:15],
        "markdownContent": full_markdown,
        "wordCount": words,
        "estimatedTokens": estimated_tokens
    }

async def fetch_and_convert(client: httpx.AsyncClient, url: str, include_images: bool, include_links: bool) -> Dict[str, Any]:
    """Fetches page content and converts it to markdown."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        resp = await client.get(url, headers=headers, timeout=15.0, follow_redirects=True)
        if resp.status_code == 200:
            parsed = html_to_clean_markdown(resp.text, include_images, include_links)
            return {
                "url": url,
                "status": "success",
                "statusCode": resp.status_code,
                **parsed
            }
        else:
            return {"url": url, "status": "failed", "statusCode": resp.status_code, "markdownContent": "", "wordCount": 0}
    except Exception as e:
        Actor.log.warning(f"Error fetching URL '{url}': {e}")
        return {"url": url, "status": "error", "error": str(e), "markdownContent": "", "wordCount": 0}

async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}
        
        start_urls = actor_input.get("startUrls", ["https://en.wikipedia.org/wiki/Artificial_intelligence"])
        max_pages = actor_input.get("maxPages", 20)
        include_images = actor_input.get("includeImages", False)
        include_links = actor_input.get("includeLinks", True)
        
        Actor.log.info(f"Starting RAG Web to Markdown Extractor with {len(start_urls)} URLs...")

        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True) as client:
            total_converted = 0
            
            for url in start_urls[:max_pages]:
                Actor.log.info(f"Converting page to Markdown: '{url}'...")
                result = await fetch_and_convert(client, url, include_images, include_links)
                
                await Actor.push_data(result)
                total_converted += 1

            Actor.log.info(f"Done! Successfully converted {total_converted} pages into clean Markdown for LLMs.")

if __name__ == "__main__":
    asyncio.run(main())
