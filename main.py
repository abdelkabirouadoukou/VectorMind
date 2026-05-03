import os
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

def load_knowledge():
    """Reads the Professeur Moncef knowledge base to use as a System Prompt."""
    file_path = "data/knowledge.md"
    if not os.path.exists(file_path):
        return "You are a highly logical and rigorous AI assistant."
    
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def load_thinking_model():
    """
    Downloads and loads a highly compressed 1.5B 'Thinking' model.
    Q4_K_M means it's compressed to 4-bit, taking only ~1.1 GB of RAM!
    """
    model_repo = "unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF"
    model_filename = "DeepSeek-R1-Distill-Qwen-1.5B-Q4_K_M.gguf"
    
    with console.status(f"[bold green]Finding or downloading {model_filename} (1.1 GB total)..."):
        # Automatically downloads and caches the model file
        model_path = hf_hub_download(repo_id=model_repo, filename=model_filename)
        
        # Load the model with optimizations for an i5 (4 cores)
        # n_ctx=2048 limits the memory usage so it easily fits in 8GB RAM
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,      # Maximum context window (input + output size)
            n_threads=4,     # Your i5 has 4 cores
            verbose=False    # Hides the messy C++ debug logs
        )
    return llm

def generate_thought_response(llm, system_prompt: str, user_input: str):
    """
    Feeds the system prompt (knowledge) and user prompt to the model.
    """
    # Instruct the AI to roleplay as Professeur Moncef using his corpus
    full_instruction = f"Roleplay as Professeur Moncef. Follow his exact philosophy and tone found here:\n\n{system_prompt}"
    
    # DeepSeek-R1 expects a specific chat structure with a system prompt
    prompt = f"<|im_start|>system\n{full_instruction}<|im_end|>\n<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"
    
    results = llm(
        prompt,
        max_tokens=600,
        stop=["<|im_end|>"],
        temperature=0.6,
        top_k=40,
        echo=False
    )
    
    return results["choices"][0]["text"]

def chat_loop():
    system_prompt = load_knowledge()
    
    welcome_text = (
        "[cyan]VectorMind: DeepSeek-R1-1.5B (Thinking Model)[/cyan]\n"
        "Persona: [bold yellow]Professeur Moncef[/bold yellow]\n"
        "Type [bold red]'exit'[/bold red] to quit."
    )
    console.print(Panel.fit(welcome_text, title="🚀 [bold blue]Welcome to VectorMind Reasoning[/bold blue]", border_style="blue"))
    
    llm = load_thinking_model()
    
    while True:
        user_input = Prompt.ask("\n[bold yellow]Étudiant[/bold yellow]")
        
        if user_input.strip().lower() == 'exit':
            console.print("[bold red]Exiting VectorMind. Goodbye![/bold red]")
            break
        
        if not user_input.strip():
            continue

        with console.status("[bold magenta]Professeur Moncef is thinking (this may take a few moments on an i5)..."):
            response = generate_thought_response(llm, system_prompt, user_input)
            
        console.print(Panel(response, title="[bold magenta]Professeur Moncef[/bold magenta]", border_style="magenta"))

if __name__ == "__main__":
    chat_loop()