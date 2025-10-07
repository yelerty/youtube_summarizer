# %%
# !pip install gradio openai langchain langchain-community youtube_transcript_api tiktoken transformers langchain-ollama

# %% [markdown]
# # YouTube Summarizer by Case Done
# - This app will get YouTube info and transcript, and allow you to summarize it.
# - It is based on LangChain map-reduce method powered by Llama 3.2 via Ollama.
# - Start by providing a valid YouTube URL in the textbox.

# %%
from youtube_transcript_api import YouTubeTranscriptApi
import re
from urllib.request import urlopen
import html
import gradio as gr
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaLLM as Ollama
import tiktoken
import sys
import json

# my libraries
from handle_notion import *

MAP_TEMPLATE_TXT = """Write a detail summary of this text section in bullet points.
Text:
{text}

SUMMARY:"""
    
COMBINE_TEMPLATE_TXT = """Combine these summaries into a final summary in bullet points.
Text:
{text}

FINAL SUMMARY:"""

def get_youtube_info(url: str):
    """Get video title and description."""
    # try:
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
        
    # Get video page content
    video_url = f"https://youtube.com/watch?v={video_id}"
    content = urlopen(video_url).read().decode('utf-8')
    
    # Extract title
    title_match = re.search(r'"title":"([^"]+)"', content)
    title = html.unescape(title_match.group(1)) if title_match else "Unknown Title"
    
    # Extract description
    desc_match = re.search(r'"description":{"simpleText":"([^"]+)"', content)
    description = html.unescape(desc_match.group(1)) if desc_match else "No description available"
    
    return title, description

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

def get_text_splitter(chunk_size: int, overlap_size: int):
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=chunk_size, chunk_overlap=overlap_size)


def get_youtube_transcript(url):
    """
    Extract transcript from a YouTube video URL.
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str: Full transcript text
    """
    try:
        # Extract video ID from URL
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")
            
        # Get transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine transcript pieces
        full_transcript = ' '.join(entry['text'] for entry in transcript_list)

        enc = tiktoken.encoding_for_model("gpt-4")
        count = len(enc.encode(full_transcript))
        
        return full_transcript, count
        
    except Exception as e:
        return f"Error: {str(e)}", 0
    

def get_llm(model: str, base_url: str, temperature: float):
    llm = Ollama(
        model=model,
        base_url=base_url,
        temperature=temperature,
    )
    return llm
    
    
def get_transcription_summary(url: str, temperature: float, chunk_size: int, overlap_size: int,
                              map_prompt_txt: str, combine_prompt_text:str):
    
    transcript, tokencount = get_youtube_transcript(url)
    docs = [Document(
        page_content=transcript,
        metadata={"source": url}
    )]

    text_splitter = get_text_splitter(chunk_size=chunk_size, overlap_size=overlap_size)
    split_docs = text_splitter.split_documents(docs)
    
    llm = get_llm(
        model="llama3.2",
        base_url="http://localhost:11434",
        temperature=temperature,
    )

    map_prompt = PromptTemplate(
        template=map_prompt_txt,
        input_variables=["text"]
    )

    combine_prompt = PromptTemplate(
        template=combine_prompt_text,
        input_variables=["text"]
    )
    
    chain = load_summarize_chain(llm, 
                                 chain_type="map_reduce",
                                 map_prompt=map_prompt,
                                 combine_prompt=combine_prompt
                                 )
    
    output = chain.invoke(split_docs)
    
    return output['output_text']


if __name__ == "__main__":
    #if len(sys.argv) < 2:
    #    print("Usage: python you_get_text.py <Youtube URL>")
    #    sys.exit(1)

    #url = sys.argv[1]
	url = get_first_unused_url()
    title, description = get_youtube_info(url)
    # full_transcript, count = get_youtube_transcript(url) 

    temperature = 0
    chunk = 4000
    overlap = 0
    map_prompt_txt = MAP_TEMPLATE_TXT
    combine_prompt_txt = COMBINE_TEMPLATE_TXT

    summeary_output = get_transcription_summary(url, temperature, chunk, overlap, map_prompt_txt, combine_prompt_txt)
    
    
    file_path = "output_title.json"
    result_data = [
        {"title:": title, "description": description,
         "summary": summeary_output}
    ]
    
    # Write the list to a JSON file
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(result_data, json_file, ensure_ascii=False, indent=4)

    print(f"Data has been written to {file_path}")



