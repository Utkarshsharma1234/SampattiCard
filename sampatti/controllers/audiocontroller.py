import os
import tempfile
from fastapi import HTTPException, UploadFile, File
import whisper
from fastapi.responses import JSONResponse
import torch

torch.cuda.is_available()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model = whisper.load_model("base", device=DEVICE)

def transcribe(file: UploadFile = File(...)):

    if not file:
        raise HTTPException(status_code=400, detail="File is not uploaded.")

    results = []

    if not os.path.exists('static'):
        os.makedirs('static')
    static_dir = os.path.join(os.getcwd(), 'static')
    try:
        with tempfile.NamedTemporaryFile(dir=static_dir, delete=True) as temp:
            temp.close()
            temp_file = open(temp.name, "wb")
            temp_file.write(file.file.read())

            result = whisper.transcribe(audio= temp.name, model=model, fp16=False)

            results.append({
                "filename": file.filename,
                "transcript": result["text"]
            })

    
    except PermissionError as e:
        print(f"Error saving temporary file: {e}")

    return JSONResponse(content={"results": results})
