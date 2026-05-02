import os
import torch
from torch.utils.data import Dataset
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    DataCollatorForLanguageModeling, 
    Trainer, 
    TrainingArguments
)

class LocalTextDataset(Dataset):
    """
    A simple custom dataset to replace the deprecated TextDataset.
    It reads a text file, tokenizes it, and splits it into blocks.
    """
    def __init__(self, tokenizer, file_path: str, block_size: int):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        tokenized_text = tokenizer.encode(text)
        self.examples = []
        # Create blocks of text
        for i in range(0, len(tokenized_text) - block_size + 1, block_size):
            self.examples.append(tokenized_text[i : i + block_size])

        # If the file is too small to make a full block, still add it
        if len(self.examples) == 0 and len(tokenized_text) > 0:
            self.examples.append(tokenized_text)
            
    def __len__(self):
        return len(self.examples)
        
    def __getitem__(self, i):
        return torch.tensor(self.examples[i], dtype=torch.long)

def load_dataset_and_collator(file_path: str, tokenizer, block_size: int = 128):
    """
    Loads the custom domain text dataset and prepares the data collator 
    for Causal Language Modeling.
    """
    dataset = LocalTextDataset(
        tokenizer=tokenizer,
        file_path=file_path,
        block_size=block_size
    )
    
    # DataCollatorForLanguageModeling automatically masks/shifts tokens to train Causal LM
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, 
        mlm=False # False for Causal LM, True for Masked LM like BERT
    )
    
    return dataset, data_collator

def fine_tune_model(
    train_file: str = "data/knowledge.txt", 
    model_name: str = "distilgpt2", 
    output_dir: str = "./models/VectorMind_v1"
):
    """
    Fine-tunes distilgpt2 locally on the specified text dataset and saves the outputs.
    """
    print(f"Loading '{model_name}' tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    if not os.path.exists(train_file):
        print(f"Error: Training file '{train_file}' not found. Please create it and add your local knowledge text.")
        # Create an empty file to help the user
        os.makedirs(os.path.dirname(train_file), exist_ok=True)
        with open(train_file, "w", encoding="utf-8") as f:
            f.write("VectorMind is a local AI engine designed to process text completely standalone.\n")
        print(f"Created a dummy '{train_file}'. Please open it and paste your actual training corpus, then re-run.")
        return

    print("Preparing dataset and collator...")
    train_dataset, data_collator = load_dataset_and_collator(train_file, tokenizer)

    # Configuration for local laptop/CPU-friendly training
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=1,                  # Keep it short for local testing
        per_device_train_batch_size=4,       # Low batch size to fit in 8GB-16GB RAM
        save_steps=500,
        save_total_limit=2,                  # Avoid filling up the hard drive
        logging_steps=50,
        use_cpu=True                         # Explicitly define fallback to CPU
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
    )

    print("Starting training process...")
    trainer.train()

    print(f"Saving the fine-tuned model to {output_dir}...")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print("Training complete! Model is ready for local offline use.")

if __name__ == "__main__":
    fine_tune_model()
