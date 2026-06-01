import os
from huggingface_hub import snapshot_download

# ComfyUI paths
CHECKPOINT_DIR = "/workspace/ComfyUI/models/checkpoints/ACE-Step"

def download_models():
    print("Downloading ACE-Step 1.5 XL models...")
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    
    try:
        # Download the entire model folder for ACE-Step 1.5 XL SFT (Supervised Fine-Tuned)
        snapshot_download(
            repo_id="ACE-Step/acestep-v15-xl-sft", 
            local_dir=CHECKPOINT_DIR,
            local_dir_use_symlinks=False
        )
        print("Model downloaded successfully.")
    except Exception as e:
        print(f"Warning: Could not download the XL model automatically: {e}")
        print("Please ensure you have enough disk space and the repo_id is correct.")

if __name__ == "__main__":
    download_models()
