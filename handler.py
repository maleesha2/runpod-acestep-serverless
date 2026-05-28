import runpod
import os
import subprocess
import time
import requests
import urllib.request
import json
import base64

# Start ComfyUI in the background
def start_comfyui():
    print("Starting ComfyUI...")
    os.chdir("/workspace/ComfyUI")
    # Run ComfyUI in background
    subprocess.Popen(["python", "main.py", "--listen", "127.0.0.1", "--port", "8188"])
    
    # Wait for ComfyUI to be ready
    max_retries = 60
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get("http://127.0.0.1:8188/system_stats")
            if response.status_code == 200:
                print("ComfyUI is ready!")
                return True
        except requests.ConnectionError:
            pass
        retries += 1
        time.sleep(1)
    print("Failed to start ComfyUI within the timeout period.")
    return False

def handler(job):
    job_input = job['input']
    workflow = job_input.get('workflow', None)
    
    if not workflow:
        return {"error": "No workflow provided in input. Please provide a ComfyUI JSON workflow."}

    # Submit the workflow to ComfyUI
    prompt_data = {"prompt": workflow}
    try:
        req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=json.dumps(prompt_data).encode('utf-8'))
        response = urllib.request.urlopen(req)
        response_data = json.loads(response.read())
        prompt_id = response_data['prompt_id']
    except Exception as e:
        return {"error": f"Failed to submit to ComfyUI: {str(e)}"}

    # Poll for completion
    timeout = 300 # 5 minutes max wait
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            history_req = urllib.request.Request(f"http://127.0.0.1:8188/history/{prompt_id}")
            history_resp = urllib.request.urlopen(history_req)
            history = json.loads(history_resp.read())
            
            # If our prompt ID is in the history, it finished
            if prompt_id in history:
                outputs = history[prompt_id].get('outputs', {})
                results = []
                
                # Iterate over outputs to find generated files
                for node_id, output in outputs.items():
                    # Ace-step usually outputs audio
                    if 'audio' in output:
                        for audio_info in output['audio']:
                            filename = audio_info['filename']
                            subfolder = audio_info.get('subfolder', '')
                            audio_path = os.path.join("/workspace/ComfyUI/output", subfolder, filename)
                            if os.path.exists(audio_path):
                                with open(audio_path, "rb") as f:
                                    audio_b64 = base64.b64encode(f.read()).decode('utf-8')
                                results.append({
                                    "filename": filename,
                                    "audio_base64": audio_b64
                                })
                                
                    # Also handle images if they generate cover art
                    elif 'images' in output:
                        for img_info in output['images']:
                            filename = img_info['filename']
                            subfolder = img_info.get('subfolder', '')
                            img_path = os.path.join("/workspace/ComfyUI/output", subfolder, filename)
                            if os.path.exists(img_path):
                                with open(img_path, "rb") as f:
                                    img_b64 = base64.b64encode(f.read()).decode('utf-8')
                                results.append({
                                    "filename": filename,
                                    "image_base64": img_b64
                                })

                return {"status": "success", "results": results}
        except Exception as e:
            print(f"Polling error: {str(e)}")
            
        time.sleep(2)

    return {"error": "Generation timed out"}

if __name__ == "__main__":
    if start_comfyui():
        # Start RunPod serverless worker
        runpod.serverless.start({"handler": handler})
    else:
        print("Exiting because ComfyUI failed to start.")
