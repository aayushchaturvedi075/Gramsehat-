import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

def generate_samples():
    output_dir = os.path.join(os.path.dirname(__file__), "sample_assets")
    os.makedirs(output_dir, exist_ok=True)
    
    # -------------------------------------------------------------
    # 1. Generate Spoken Hindi Audio Clip (.wav, .mp3, .webm)
    # -------------------------------------------------------------
    hindi_text = "नमस्ते डॉक्टर साहब, मुझे पिछले दो दिनों से तेज़ बुखार, खांसी और बदन दर्द हो रहा है।"
    temp_aiff = os.path.join(output_dir, "temp_hindi.aiff")
    hindi_wav = os.path.join(output_dir, "hindi_symptom_audio.wav")
    hindi_mp3 = os.path.join(output_dir, "hindi_symptom_audio.mp3")
    hindi_webm = os.path.join(output_dir, "hindi_symptom_audio.webm")
    
    # Locate ffmpeg
    try:
        import imageio_ffmpeg
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        ffmpeg_bin = "ffmpeg"
        
    print(f"Generating Hindi speech using macOS Lekha voice: '{hindi_text}'")
    try:
        # Rate -r 135 for natural, clear spoken cadence
        subprocess.run(["say", "-r", "135", "-v", "Lekha", "-o", temp_aiff, hindi_text], check=True)
        # Convert to WAV (16kHz mono, standard speech processing format)
        subprocess.run([ffmpeg_bin, "-y", "-i", temp_aiff, "-ar", "16000", "-ac", "1", hindi_wav], check=True, stderr=subprocess.DEVNULL)
        # Convert to MP3
        subprocess.run([ffmpeg_bin, "-y", "-i", temp_aiff, "-b:a", "64k", hindi_mp3], check=True, stderr=subprocess.DEVNULL)
        # Convert to WebM
        subprocess.run([ffmpeg_bin, "-y", "-i", temp_aiff, "-c:a", "libopus", hindi_webm], check=True, stderr=subprocess.DEVNULL)
        if os.path.exists(temp_aiff):
            os.remove(temp_aiff)
        print(f"✓ Created sample audio files: {hindi_wav}, {hindi_mp3}, {hindi_webm}")
    except Exception as e:
        print(f"Warning: Failed to generate audio with 'say': {e}")
        # Fallback: create a basic sinusoidal WAV tone for testing if TTS unavailable
        import wave, struct, math
        with wave.open(hindi_wav, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            data = [int(1000 * math.sin(2 * math.pi * 440 * i / 16000)) for i in range(16000)]
            wf.writeframes(struct.pack(f"<{len(data)}h", *data))
        print("✓ Created synthetic fallback WAV audio.")

    # -------------------------------------------------------------
    # 2. Generate Sample Printed Hindi & English Prescription Image
    # -------------------------------------------------------------
    img_width, img_height = 900, 680
    img = Image.new("RGB", (img_width, img_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Kohinoor.ttc",
        "/System/Library/Fonts/Supplemental/DevanagariMT.ttc"
    ]
    
    header_font = None
    body_font = None
    sub_font = None
    
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                header_font = ImageFont.truetype(fp, 26)
                body_font = ImageFont.truetype(fp, 20)
                sub_font = ImageFont.truetype(fp, 16)
                print(f"Using high-quality Unicode font: {fp}")
                break
            except Exception:
                continue

    if not body_font:
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()

    # Draw prescription outer border
    draw.rectangle([(20, 20), (img_width - 20, img_height - 20)], outline=(40, 40, 40), width=2)
    # Header box
    draw.rectangle([(25, 25), (img_width - 25, 110)], fill=(240, 246, 255), outline=(180, 200, 230), width=1)
    
    draw.text((40, 35), "GRAMSEHAT RURAL HEALTH CLINIC", fill=(10, 40, 100), font=header_font)
    draw.text((40, 72), "प्राथमिक स्वास्थ्य केंद्र (Primary Health Centre)", fill=(30, 60, 120), font=sub_font)
    
    # Patient info
    draw.line([(25, 115), (img_width - 25, 115)], fill=(200, 200, 200), width=2)
    draw.text((40, 125), "Patient Name: Ram Lal | Age: 48 Yrs | Gender: Male", fill=(20, 20, 20), font=body_font)
    draw.text((40, 155), "Vitals: BP 130/85 mmHg | Pulse 78 bpm | Temp 100.8 F", fill=(20, 20, 20), font=body_font)
    draw.line([(25, 190), (img_width - 25, 190)], fill=(180, 180, 180), width=1)
    
    # Prescription items (Bilingual)
    draw.text((40, 205), "Rx (Prescribed Medications):", fill=(140, 15, 15), font=header_font)
    
    rx_items = [
        "1. Tab Paracetamol 650mg - 1 गोली दिन में दो बार",
        "   (खाना खाने के बाद / After meals - 3 Days)",
        "2. Tab Cetirizine 10mg - 1 गोली रात को",
        "3. Syrup Cough Relief - 10ml दिन में तीन बार",
        "4. ORS घोल - 2 पैकेट पानी में मिलाकर पिएं",
        "",
        "Lab Investigation: Blood Sugar Fasting: 95 mg/dL (Normal)",
        "Follow up: यदि 3 दिन में बुखार कम न हो तो तुरंत संपर्क करें।"
    ]
    
    y = 250
    for line in rx_items:
        draw.text((50, y), line, fill=(15, 15, 15), font=body_font)
        y += 36

    # Doctor signature footer
    draw.text((img_width - 260, img_height - 65), "Dr. Sharma (MBBS)", fill=(50, 50, 50), font=body_font)
    
    prescription_path = os.path.join(output_dir, "sample_prescription.png")
    img.save(prescription_path, "PNG")
    print(f"✓ Created sample prescription image: {prescription_path}")

    # -------------------------------------------------------------
    # 3. Generate Blank / No-Text Image (to test 422 graceful error)
    # -------------------------------------------------------------
    blank_img = Image.new("RGB", (400, 300), color=(180, 180, 185))
    blank_path = os.path.join(output_dir, "sample_blank_image.png")
    blank_img.save(blank_path, "PNG")
    print(f"✓ Created blank image: {blank_path}")

    # -------------------------------------------------------------
    # 4. Generate Corrupted Audio File (to test 422 graceful error)
    # -------------------------------------------------------------
    corrupt_audio_path = os.path.join(output_dir, "sample_corrupt_audio.wav")
    with open(corrupt_audio_path, "wb") as f:
        f.write(b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00corrupted_audio_data_stream_garbage_noise")
    print(f"✓ Created corrupt audio file: {corrupt_audio_path}")

    print("\nAll test sample assets generated successfully!")

if __name__ == "__main__":
    generate_samples()
