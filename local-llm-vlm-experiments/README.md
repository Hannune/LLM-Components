# Local LLM Vision-Language Model (VLM) Experiments

**Experiment with vision-language models running 100% locally - analyze images with LLMs on your own hardware**

Test and compare different VLM approaches: Ollama-based models (llama3.2-vision, gemma3) and Hugging Face models (Granite Vision) with quantization support.

## Features

- **100% Local Inference** - No API costs, complete privacy
- **Multiple Backends** - Ollama API and Transformers
- **Quantization Support** - 4-bit/8-bit for consumer GPUs
- **Interactive Testing** - Command-line interface for quick experiments
- **Custom Prompts** - System prompts for specialized tasks

## Supported Models

### Ollama Models (Easy Setup)
- `llama3.2-vision:latest` - Meta's vision model
- `llava:7b` - LLaVA vision model
- `gemma3:12b` - Google's multimodal model

### Hugging Face Models (More Control)
- `ibm-granite/granite-vision-3.2-2b` - IBM Granite Vision
- Any Vision2Seq model on Hugging Face

## Quick Start

### 1. Setup Ollama (Easiest)

```bash
# Install dependencies
pip install -r requirements.txt

# Pull a VLM model in Ollama
ollama pull llama3.2-vision

# Configure
cp .env.example .env
# Edit IMAGE_PATH in .env

# Run
python ollama_vlm_example.py
```

### 2. Setup Granite Vision (More Features)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Set GRANITE_MODEL_PATH and IMAGE_PATH

# Run (downloads model automatically)
python granite_vision_example.py
```

## Usage

### Ollama VLM Example

```python
from ollama import Client

client = Client(host="http://localhost:11434")

messages = [{
    'role': 'user',
    'content': 'Describe this image',
    'images': ['photo.jpg']
}]

response = client.chat(
    model="llama3.2-vision",
    messages=messages
)

print(response["message"]["content"])
```

### Granite Vision Example

```python
from transformers import AutoProcessor, AutoModelForVision2Seq
import torch

model_id = "ibm-granite/granite-vision-3.2-2b"
processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForVision2Seq.from_pretrained(model_id).to("cuda")

conversation = [
    {
        "role": "user",
        "content": [
            {"type": "image", "url": "photo.jpg"},
            {"type": "text", "text": "What's in this image?"},
        ],
    },
]

inputs = processor.apply_chat_template(
    conversation, tokenize=True, return_tensors="pt"
).to("cuda")

output = model.generate(**inputs, max_new_tokens=100)
print(processor.decode(output[0]))
```

## Examples

### Example 1: Simple Image Description
```bash
python ollama_vlm_example.py
```

Asks: "Describe what you see in this image"

### Example 2: Safety Risk Assessment
Custom system prompt for specialized analysis:
```python
system_prompt = (
    "You are a safety inspector. "
    "Rate risks 0-10 and explain concerns."
)
```

### Example 3: Interactive Mode
Ask multiple questions about the same image in real-time.

## Configuration

Edit `.env`:

```bash
# Choose your backend
OLLAMA_HOST=http://localhost:11434
VLM_MODEL=llama3.2-vision:latest

# Or use Granite Vision
GRANITE_MODEL_PATH=ibm-granite/granite-vision-3.2-2b

# Enable quantization (reduces VRAM)
USE_4BIT_QUANT=true

# Your test image
IMAGE_PATH=path/to/image.jpg
```

## Quantization (Save VRAM)

### 4-bit Quantization
Best for consumer GPUs (8GB+ VRAM):
```bash
USE_4BIT_QUANT=true
```

Memory usage:
- Granite 2B: ~2GB VRAM (4-bit) vs ~4GB (FP16)
- Quality loss: Minimal (<5%)

### 8-bit Quantization
More quality, more VRAM:
```bash
USE_8BIT_QUANT=true
```

## Use Cases

### 1. Image Understanding
```python
query = "Describe everything you see in detail"
```

### 2. Object Detection
```python
query = "List all objects and their locations"
```

### 3. Safety Monitoring
```python
query = "Identify any safety hazards in this scene"
```

### 4. Document Analysis
```python
query = "Extract all text and explain the document structure"
```

### 5. Medical Imaging (Experimental)
```python
query = "Describe any abnormalities visible in this scan"
```

## Performance Benchmarks

### Ollama llama3.2-vision (11B)
- Hardware: RTX 4090
- VRAM: 22GB
- Speed: ~2-3 seconds per image
- Quality: Excellent

### Granite Vision 2B (4-bit)
- Hardware: RTX 3090
- VRAM: 2GB
- Speed: ~1-2 seconds per image
- Quality: Good for size

## Troubleshooting

### Ollama model not found
```bash
# List available models
ollama list

# Pull the model
ollama pull llama3.2-vision
```

### Out of memory (CUDA OOM)
Enable quantization:
```bash
USE_4BIT_QUANT=true
```

Or use smaller model:
```bash
VLM_MODEL=llava:7b  # Instead of 13b
```

### Image not loading
Check paths:
```python
import os
print(os.path.abspath("your_image.jpg"))
```

Supported formats: JPG, PNG, WEBP

### Slow inference
- Use quantization (4-bit/8-bit)
- Reduce max_new_tokens
- Use smaller models
- Check GPU is being used: `torch.cuda.is_available()`

## Comparison: Ollama vs Transformers

| Feature | Ollama | Transformers |
|---------|---------|--------------|
| Setup | Easier | More complex |
| Speed | Fast | Fast |
| VRAM | Lower | Higher |
| Flexibility | Limited | Full control |
| Models | Curated | Any HF model |
| Best For | Quick tests | Production |

## Model Recommendations

### For Beginners
- `llama3.2-vision` via Ollama - Easy setup, great quality

### For Low VRAM (8GB)
- `llava:7b` via Ollama
- Granite 2B with 4-bit quantization

### For Best Quality
- `llama3.2-vision:latest` (11B)
- Granite Vision 8B (if available)

### For Speed
- Granite 2B with 4-bit quant
- llava:7b

## Future Experiments

- [ ] Compare multiple VLMs side-by-side
- [ ] Batch processing for multiple images
- [ ] Fine-tuning on custom datasets
- [ ] Video frame analysis
- [ ] OCR comparison tests

## Requirements

- Python 3.8+
- NVIDIA GPU (6GB+ VRAM recommended)
- Ollama (for Ollama examples)
- CUDA 11.8+

## License

MIT
