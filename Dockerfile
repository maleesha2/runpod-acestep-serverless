FROM runpod/pytorch:2.2.1-py3.10-cuda12.1.1-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /workspace/ComfyUI

# Install ComfyUI dependencies
RUN pip install --no-cache-dir -r /workspace/ComfyUI/requirements.txt

# Clone ACE-Step Custom Node
WORKDIR /workspace/ComfyUI/custom_nodes
RUN git clone https://github.com/ace-step/ACE-Step-ComfyUI.git

# Install ACE-Step dependencies
WORKDIR /workspace/ComfyUI/custom_nodes/ACE-Step-ComfyUI
# In case they have a requirements.txt, we install it. Otherwise we install known deps.
RUN if [ -f "requirements.txt" ]; then pip install --no-cache-dir -r requirements.txt; else pip install --no-cache-dir librosa soundfile; fi

# Install runpod SDK and requests for the handler
RUN pip install --no-cache-dir runpod requests huggingface_hub

# Copy our custom scripts
WORKDIR /workspace
COPY download_models.py /workspace/download_models.py
COPY handler.py /workspace/handler.py
COPY start.sh /workspace/start.sh
RUN chmod +x /workspace/start.sh

# Download models during build so the serverless image boots fast
RUN python3 /workspace/download_models.py

# Set entrypoint
CMD ["/workspace/start.sh"]
