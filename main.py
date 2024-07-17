from fastapi import FastAPI, File, UploadFile
import easyocr
import os
import re
import cv2
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import google.generativeai as genai
import PIL.Image

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

@app.post('/scan-kis')
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

    print(result)


    return JSONResponse(
        {
            'result': result
        },
        
    )

@app.post('/scan-bpjs')
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

    print(result)


    return JSONResponse(
        {
            'result': result
        },
        
    )

@app.post('/scan-bpjs-gemini')
async def scan_image_gemini(file: UploadFile):
   
    filename = file.filename
    file_ext = filename.rsplit('.', 1)[1].lower()
    file_name = f'image.{file_ext}'
    with open(file_name, 'wb') as buffer:
        contents = await file.read()
        buffer.write(contents)
    
    
    genai.configure(api_key='AIzaSyDG_Xhy4jDpbuITKkccIPJdO4vXM0POLLk') 

   
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="Anda adalah system text recognition untuk membaca kartu bpjs, meliputi no kartu, nama, tanggal lahir, nik, faskes tingkat 1 lalu kelas rawat, selain itu tidak diperlukan, berikan raw datanya, dan tidak usah di parsing"
    )

   
    img = PIL.Image.open(file_name)
    response = model.generate_content(img)
    
   
    os.remove(file_name)

    pattern = r"(\d{13})\n(.+)\n(\d{2}-\d{2}-\d{4})\n(\d{16})\n(.+)\n(.+)"
    match = re.search(pattern, response.text)
    if match:
        no_kartu = match.group(1)
        nama = match.group(2)
        tanggal_lahir = match.group(3)
        nik = match.group(4)
        faskes = match.group(5)
        kelas_rawat = match.group(6)

        parsed_result = {
            "no_kartu": no_kartu,
            "nama": nama,
            "tanggal_lahir": tanggal_lahir,
            "nik": nik,
            "faskes": faskes,
            "kelas_rawat": kelas_rawat,
        }

        return JSONResponse(parsed_result)
    else:
        parsed_result = {
            "no_kartu": "gagal terdeteksi",
            "nama":  "gagal terdeteksi",
            "tanggal_lahir":  "gagal terdeteksi",
            "nik":  "gagal terdeteksi",
            "faskes":  "gagal terdeteksi",
            "kelas_rawat":  "gagal terdeteksi",
        }

        return JSONResponse(parsed_result)
    
    

@app.post('/scan-kis-gemini')
async def scan_image_gemini(file: UploadFile):

    filename = file.filename
    file_ext = filename.rsplit('.', 1)[1].lower()
    file_name = f'image.{file_ext}'
    with open(file_name, 'wb') as buffer:
        contents = await file.read()
        buffer.write(contents)
    

    genai.configure(api_key='AIzaSyDG_Xhy4jDpbuITKkccIPJdO4vXM0POLLk') # Ganti dengan kunci API Google Anda

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="Anda adalah system text recognition untuk membaca kartu bpjs, meliputi no kartu, nama, tanggal lahir, nik, faskes tingkat 1 lalu kelas rawat, selain itu tidak diperlukan, berikan raw datanya, dan tidak usah di parsing"
    )

    img = PIL.Image.open(file_name)
    response = model.generate_content(img)
    
    os.remove(file_name)

    data = {
        "no_kartu": "Tidak terdeteksi",
        "nama": "Tidak terdeteksi",
        "alamat": "Tidak terdeteksi",
        "tanggal_lahir": "Tidak terdeteksi",
        "nik": "Tidak terdeteksi",
        "faskes": "Tidak terdeteksi"
    }

    # Asumsi: data dipisah dengan baris baru
    lines = response.text.splitlines()

    # Looping melalui setiap baris dan mencocokkan dengan kunci yang diharapkan
    for i, line in enumerate(lines):
        line = line.strip()
        if "Nomor Kartu" in line:
            data["no_kartu"] = line.split(":")[-1].strip()
        elif "Nama" in line:
            data["nama"] = line.split(":")[-1].strip()
        elif "Alamat" in line:
            data["alamat"] = line.split(":")[-1].strip()
        elif "Tanggal" in line:
            data["tanggal_lahir"] = line.split(":")[-1].strip()
        elif "NIK" in line:
            data["nik"] = line.split(":")[-1].strip()
        elif "Faskes" in line:
            data["faskes"] = line.split(":")[-1].strip()

    return JSONResponse(data)




if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)