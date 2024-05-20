from fastapi import FastAPI, File, UploadFile
import easyocr
import os
import re
import cv2
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
reader = easyocr.Reader(['id'], gpu=True)
ALLOWED_EXTENSIONS = {'jpg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post('/scan')
async def scan_image(file: UploadFile = File(...)):
    if not file:
        return JSONResponse({'error': 'No file proviRded'}, status_code=400)
    
    filename = file.filename
    if not allowed_file(filename):
        return JSONResponse({'error': 'Invalid file format'}, status_code=400)
    
    file_ext = filename.rsplit('.', 1)[1].lower()
    file_name = f'image.{file_ext}'
    
    with open(file_name, 'wb') as buffer:
        contents = await file.read()
        buffer.write(contents)
    
    img = cv2.imread(file_name)
    result = reader.readtext(img, detail=0)
    os.remove(file_name)

    return JSONResponse(
        {
            'result': result
        },
        
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)