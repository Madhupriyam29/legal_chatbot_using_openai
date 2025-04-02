"""
Legal Assistant Chatbot  
This script implements a chatbot designed to assist with legal queries.  
It leverages OpenAI's API to generate responses based on user input and relevant legal documents.  
"""

import os
import sys
import fitz  # PyMuPDF
from openai import OpenAI
from dotenv import load_dotenv

# System prompt for the legal chatbot

def create_system_prompt(judgment_text=""):
    return f"""
You are an expert legal assistant with extensive knowledge of laws, procedures, and legal interpretation.
JUDGMENT CONTEXT:
{judgment_text}
Your expertise includes:
- Statutory interpretation and application
- Case law analysis and precedent
- Legal procedure and strategy
- Contract law and interpretation
- Civil and criminal litigation
- Regulatory compliance
- Industry-specific legal frameworks

When responding to queries:
1. Provide practical, actionable insights based on the judgment text when relevant.
2. Reference specific sections of the judgment or related laws when appropriate.
3. Use polite, professional legal terminology that practicing lawyers would appreciate.
4. Acknowledge jurisdictional considerations when relevant.
5. Maintain a balanced, objective analysis of legal issues.
6. Clarify when a question requires additional context or jurisdiction-specific analysis.
7. Present potential arguments from multiple perspectives when appropriate.

Your tone should be:
- Professional but conversational
- Precise without excessive jargon
- Respectful of legal traditions
- Thoughtful and measured
- Confident but not absolute in areas of legal ambiguity

Remember that your responses should be relevant to legal practice, practical for lawyers, clear and well-defined, demonstrate depth of knowledge, and be applicable to real-world legal scenarios.
You should not provide legal advice that establishes an attorney-client relationship, and you should clarify that your responses are for informational purposes only.
"""

def initialize_openai():
    """
    Initialize the OpenAI API with credentials from environment variables.
    """
    load_dotenv()
    if "OPENAI_API_KEY" not in os.environ:
        raise ValueError("OPENAI_API_KEY environment variable not found. Please check your .env file.")
    
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    print("OpenAI client initialized successfully.")
    return client

def chat_with_openai(client, judgment_text=""):
    """
    Start an interactive chat session with the OpenAI API.
    
    Args:
        client: OpenAI client object
        judgment_text: Optional text of a legal judgment to analyze
    """
    system_prompt = create_system_prompt(judgment_text)
    messages = [{"role": "system", "content": system_prompt}]
    
    print("\n" + "="*50)
    print("LEGAL ASSISTANT CHAT")
    print("="*50)
    print("Type 'exit', 'quit', or 'q' to end the conversation.")
    print("Type 'load judgment' to load a judgment from a file.")
    print("Type 'clear' to start a new conversation.")
    print("-"*50)
    
    if judgment_text:
        print("\nJudgment loaded successfully. You can now ask questions about it.")
        print(f"Document length: {len(judgment_text.split())} words")
        print("-"*50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\nGoodbye! Thank you for using the Legal Assistant.")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() == "clear":
            messages = [{"role": "system", "content": system_prompt}]
            print("\nConversation cleared. Starting fresh.")
            continue
        
        messages.append({"role": "user", "content": user_input})
        
        try:
            print("\nThinking...", end="", flush=True)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
            )
            print("\r" + " " * 12 + "\r", end="", flush=True)
            assistant_response = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_response})
            print("\nAssistant:\n")
            print(assistant_response)
            print("\n" + "-"*50)
        except Exception as e:
            print(f"\nError: {e}")
            print("\n" + "-"*50)

def extract_text_from_file(file_path):
    """
    Extract text from a file, supporting both PDF and text files.
    """
    try:
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist")
            return ""
        
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.pdf':
            return extract_text_from_pdf(file_path)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"Error extracting text from file: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using PyMuPDF.
    """
    try:
        print(f"Extracting text from PDF: {pdf_path}")
        doc = fitz.open(pdf_path)
        full_text = [page.get_text() for page in doc]
        doc.close()
        return "\n\n".join(full_text)
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

if __name__ == "__main__":
    try:
        openai_client = initialize_openai()
        judgment_file = "data/DelhiHC_March_2025[1].pdf"
        print(f"Loading judgment from: {judgment_file}")
        judgment_text = extract_text_from_file(judgment_file)
        if not judgment_text:
            print("Warning: No text could be extracted from the judgment file.")
        chat_with_openai(openai_client, judgment_text)
    except Exception as e:
        print(f"Critical Error: {e}")