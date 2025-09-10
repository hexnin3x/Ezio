import asyncio
import os
import json # Import the json library to read API error messages
from random import randint
from time import sleep

import requests
from dotenv import get_key
from PIL import Image

def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ","_")

    Files = [f"{prompt}{i}.jpg" for i in range(1,5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
           # Try to open and display the image
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1) # Pause for 1 second before showing the next image

        except IOError:
            print(f"Unable to open {image_path}")

# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Async function to send a query to the Hugging Face API
async def query(payload):
    # This function now checks for API errors before returning content.
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    
    # CRITICAL FIX: Check if the API response is a valid image.
    if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
        return response.content
    else:
        # If it's not an image, it's an error. Print the error and return None.
        try:
            error_data = response.json()
            print(f"API Error: {error_data.get('error', 'Unknown error')}")
        except json.JSONDecodeError:
            print(f"API Error: Received non-JSON response (status code {response.status_code})")
        return None

# Async function to generate images based on the given prompt
async def generate_images(prompt: str):
    tasks = []
    
    # Create 4 image generation tasks
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra high details, high resolution, seed = {randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
        
    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)

    # Ensure the target directory exists before saving
    os.makedirs("Data", exist_ok=True)
    for i, image_bytes in enumerate(image_bytes_list):
        # CRITICAL FIX: Only write the file if image_bytes is not None (i.e., no API error occurred)
        if image_bytes:
            with open(fr"Data\{prompt.replace(' ','_')}{i + 1}.jpg", "wb") as f:
                f.write(image_bytes)

# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt)) # Run the async image generation
    open_images(prompt) # Open the generated images

# Main loop to monitor for image generation requests
while True:
    
    try:
        # Read the status and prompt from the data file
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()
            
        Prompt, Status = Data.split(",")

        if Status == "True":
            print("genrating images...")
            ImageStatus = GenerateImages(prompt=Prompt)

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")
                break

        else:
            sleep(1)

    # This temporary block remains unchanged as requested.
    except Exception:
        pass
        
        