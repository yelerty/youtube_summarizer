#!/usr/bin/env python
# -*- coding: utf-8 -*-

from youtube_transcript_api import YouTubeTranscriptApi
import re
from urllib.request import urlopen
import html
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaLLM as Ollama
import sys

MAP_TEMPLATE = """Write a detail summary of this text section in bullet points.
Text:
{text}

SUMMARY:"""

COMBINE_TEMPLATE = """Combine these summaries into a final summary in bullet points.
Text:
{text}

FINAL SUMMARY:"""

TRANSLATE_TEMPLATE = """Translate the following summary to Korean. Keep the bullet point format.

Original summary:
{text}

Korean translation:"""

def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_youtube_transcript(url):
    """Extract transcript from a YouTube video URL."""
    try:
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        # Get transcript using the new API
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=['ko', 'en', 'ja', 'zh'])
        full_transcript = ' '.join(entry.text for entry in transcript)

        return full_transcript

    except Exception as e:
        import traceback
        return f"Error: {str(e)}\n{traceback.format_exc()}"

def get_text_splitter(chunk_size: int, overlap_size: int):
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size,
        chunk_overlap=overlap_size
    )

def get_llm(model: str, temperature: float):
    llm = Ollama(
        model=model,
        temperature=temperature,
    )
    return llm

def summarize_transcript(url: str, temperature: float = 0, chunk_size: int = 4000,
                        overlap_size: int = 0):
    """Summarize YouTube video transcript and translate to Korean."""

    print(f"Fetching transcript from: {url}")
    transcript = get_youtube_transcript(url)

    if transcript.startswith("Error:"):
        return transcript

    print("Creating document chunks...")
    docs = [Document(page_content=transcript, metadata={"source": url})]
    text_splitter = get_text_splitter(chunk_size=chunk_size, overlap_size=overlap_size)
    split_docs = text_splitter.split_documents(docs)

    print(f"Processing {len(split_docs)} chunks with Llama model...")
    llm = get_llm(model="llama3.2", temperature=temperature)

    # Always summarize in English first
    map_prompt = PromptTemplate(template=MAP_TEMPLATE, input_variables=["text"])
    combine_prompt = PromptTemplate(template=COMBINE_TEMPLATE, input_variables=["text"])

    chain = load_summarize_chain(
        llm,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=combine_prompt
    )

    output = chain.invoke(split_docs)
    summary = output['output_text']

    # Translate the summary to Korean
    print("Translating summary to Korean...")
    translate_prompt = PromptTemplate(template=TRANSLATE_TEMPLATE, input_variables=["text"])
    translation = llm.invoke(translate_prompt.format(text=summary))

    return translation

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python summarize.py <YouTube URL>")
        sys.exit(1)

    url = sys.argv[1]

    try:
        summary = summarize_transcript(url)
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(summary)
        print("="*80 + "\n")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
