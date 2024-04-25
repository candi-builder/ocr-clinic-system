from fastapi import FastAPI, File, UploadFile
import easyocr
import os

from fastapi.responses import JSONResponse

app = FastAPI()
reader = easyocr.Reader(['id'], gpu=False)
ALLOWED_EXTENSIONS = {'jpg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post('/scan')
async def scan_image(file: UploadFile = File(...)):
    if not file:
        return JSONResponse({'error': 'No file provided'}, status_code=400)
    
    filename = file.filename
    if not allowed_file(filename):
        return JSONResponse({'error': 'Invalid file format'}, status_code=400)
    
    file_ext = filename.rsplit('.', 1)[1].lower()
    file_name = f'image.{file_ext}'
    
    with open(file_name, 'wb') as buffer:
        contents = await file.read()
        buffer.write(contents)
    
    result = reader.readtext(file_name, detail=0)
    os.remove(file_name)

   
    
    return JSONResponse({'message': result})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)