"""
Granite Vision 3.2 VLM Example - LOCAL INFERENCE

Run IBM Granite Vision models locally with Transformers.
Supports quantization for consumer GPUs.
"""

import os
from transformers import AutoProcessor, AutoModelForVision2Seq, BitsAndBytesConfig
import torch
import time
from dotenv import load_dotenv

load_dotenv()

device = "cuda" if torch.cuda.is_available() else "cpu"

# Model configuration
MODEL_PATH = os.getenv("GRANITE_MODEL_PATH", "ibm-granite/granite-vision-3.2-2b")
IMAGE_PATH = os.getenv("IMAGE_PATH", "example.jpg")

# Quantization options
USE_4BIT = os.getenv("USE_4BIT_QUANT", "false").lower() == "true"
USE_8BIT = os.getenv("USE_8BIT_QUANT", "false").lower() == "true"


def load_model():
    """Load Granite Vision model with optional quantization."""
    processor = AutoProcessor.from_pretrained(MODEL_PATH)
    
    if USE_4BIT:
        print("Loading with 4-bit quantization")
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        model = AutoModelForVision2Seq.from_pretrained(
            MODEL_PATH,
            quantization_config=quantization_config,
            device_map="auto"
        )
    elif USE_8BIT:
        print("Loading with 8-bit quantization")
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)
        model = AutoModelForVision2Seq.from_pretrained(
            MODEL_PATH,
            quantization_config=quantization_config,
            device_map="auto"
        )
    else:
        print("Loading in full precision")
        model = AutoModelForVision2Seq.from_pretrained(MODEL_PATH).to(device)
    
    return processor, model


def analyze_image(processor, model, image_path, query):
    """Analyze image with text query."""
    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "image", "url": image_path},
                {"type": "text", "text": query},
            ],
        },
    ]
    
    inputs = processor.apply_chat_template(
        conversation,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt"
    ).to(device)
    
    output = model.generate(**inputs, max_new_tokens=100)
    return processor.decode(output[0], skip_special_tokens=True)


def main():
    print(f"Loading model: {MODEL_PATH}")
    processor, model = load_model()
    
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image not found at {IMAGE_PATH}")
        print("Set IMAGE_PATH environment variable")
        return
    
    while True:
        query = input("\nAsk about the image (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        
        print("Processing...")
        start_time = time.time()
        
        response = analyze_image(processor, model, IMAGE_PATH, query)
        
        print(f"\nResponse: {response}")
        print(f"Time: {time.time() - start_time:.2f}s")


if __name__ == "__main__":
    main()
