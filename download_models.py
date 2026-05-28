import os
from huggingface_hub import hf_hub_download

# ComfyUI paths
CHECKPOINT_DIR = "/workspace/ComfyUI/models/checkpoints"

def download_models():
    print("Downloading ACE-Step models...")
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    
    # Download the main ACE-Step model
    # Note: Replace repo_id and filename if ACE-Step hosts models at a different specific HuggingFace location.
    # Currently assuming a generic path based on standard practices for these custom nodes.
    try:
        hf_hub_download(
            repo_id="ACE-Step/ACE-Step-1.5", 
            filename="acestep_1.5.safetensors",
            local_dir=CHECKPOINT_DIR
        )
        print("Model downloaded successfully.")
    except Exception as e:
        print(f"Warning: Could not download the default model automatically: {e}")
        print("Please ensure the HuggingFace repo_id and filename match the official release.")

if __name__ == "__main__":
    download_models()
