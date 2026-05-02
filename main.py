import torch
from transformers import pipeline, set_seed
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

import os

# Initialize rich console for UI
console = Console()

def load_model(model_name: str = "distilgpt2"):
    """
    Loads the text generation pipeline locally.
    Uses the fine-tuned VectorMind model if it exists, otherwise falls back to distilgpt2.
    """
    # Check if the fine-tuned model exists
    if os.path.exists("./models/VectorMind_v1"):
        model_name = "./models/VectorMind_v1"
        
    with console.status(f"[bold green]Loading {model_name} model locally (this may take a moment)..."):
        # device=-1 explicitly forces CPU, adjust to 0 for CUDA if available
        generator = pipeline('text-generation', model=model_name, device=-1)
    return generator

def generate_text(generator, prompt: str, max_length: int = 150) -> str:
    """
    Takes a string prompt and returns AI-generated text using professional 
    sampling parameters (temperature=0.8, top_k=50).
    """
    results = generator(
        prompt,
        max_length=max_length,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.8,
        top_k=50,
        pad_token_id=generator.tokenizer.eos_token_id
    )
    # The pipeline returns a list of dicts. We extract the generated text.
    return results[0]["generated_text"]

def chat_loop():
    """
    Implements a rich-based terminal loop that allows the user 
    to chat with the model until they type 'exit'.
    """
    welcome_text = (
        "[cyan]Your fully local, offline text generation engine.[/cyan]\n"
        "Model: [bold]distilgpt2[/bold]\n"
        "Type [bold red]'exit'[/bold red] to quit."
    )
    console.print(Panel.fit(welcome_text, title="🚀 [bold blue]Welcome to VectorMind[/bold blue]", border_style="blue"))
    
    generator = load_model()
    
    while True:
        user_input = Prompt.ask("\n[bold yellow]You[/bold yellow]")
        
        if user_input.strip().lower() == 'exit':
            console.print("[bold red]Exiting VectorMind. Goodbye![/bold red]")
            break
        
        if not user_input.strip():
            continue

        with console.status("[bold green]VectorMind is generating text..."):
            response = generate_text(generator, user_input)
        
        console.print(Panel(response, title="[bold magenta]VectorMind[/bold magenta]", border_style="magenta"))

if __name__ == "__main__":
    # Ensure reproducible results, optional but good practice
    set_seed(42)
    # Launch chat loop
    chat_loop()
