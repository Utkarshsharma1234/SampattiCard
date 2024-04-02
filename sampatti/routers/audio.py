from fastapi import APIRouter, UploadFile, File
import whisper
import torch
from ..controllers import audiocontroller

torch.cuda.is_available()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model = whisper.load_model("base", device=DEVICE)

router = APIRouter(
    tags= ["whisper"]
)

@router.post("/transcribe")
def transcribe(file: UploadFile = File(...)):
    return audiocontroller.transcribe(file=file)