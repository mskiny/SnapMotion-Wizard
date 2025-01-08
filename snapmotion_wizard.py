import cv2
import os
import sys
import shutil
import subprocess
from tqdm import tqdm
from PIL import Image
import numpy as np
from pathlib import Path

def get_ffmpeg_path():
    """Get the path to the local FFmpeg executable"""
    if sys.platform == "win32":
        ffmpeg_path = Path(__file__).parent / "bin" / "ffmpeg" / "ffmpeg.exe"
    else:
        ffmpeg_path = Path(__file__).parent / "bin" / "ffmpeg" / "ffmpeg"
    return str(ffmpeg_path)

def create_video_with_ffmpeg(image_folder, output_path, frame_duration, resize=None):
    """
    Create a video using FFmpeg from a folder of numbered frames.
    """
    ffmpeg_path = get_ffmpeg_path()
    if not os.path.exists(ffmpeg_path):
        raise RuntimeError(
            "FFmpeg not found in bin folder. Please ensure FFmpeg is installed in the project's bin directory."
        )

    # Create temporary folder for frames
    temp_dir = Path(output_path).parent / "temp_frames"
    temp_dir.mkdir(exist_ok=True)

    try:
        # First pass: Convert and copy all images to temp directory
        print("\n📥 Processing images...")
        for idx, image_file in enumerate(tqdm(image_files, desc="Preparing frames")):
            with Image.open(image_file) as img:
                # Convert to RGB mode to ensure consistency
                img = img.convert('RGB')
                if resize:
                    img = img.resize(resize, Image.Resampling.LANCZOS)
                # Save as PNG with sequential numbering
                save_path = temp_dir / f"frame_{idx:06d}.png"
                img.save(save_path, "PNG")

        # Second pass: Create video with FFmpeg
        print("\n🎬 Creating video...")
        cmd = [
            ffmpeg_path,
            '-y',  # Overwrite output file if it exists
            '-framerate', f'{1/frame_duration}',
            '-i', str(temp_dir / 'frame_%06d.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-crf', '23',  # Quality setting (0-51, lower is better)
            '-preset', 'medium',  # Encoding speed preset
            output_path
        ]
        
        # Run FFmpeg
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # Show progress
        with tqdm(total=100, desc="Encoding video") as pbar:
            last_percent = 0
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                if "time=" in line:
                    try:
                        # Extract time information and update progress
                        time_str = line.split("time=")[1].split()[0]
                        h, m, s = map(float, time_str.split(':'))
                        current_seconds = h * 3600 + m * 60 + s
                        total_seconds = len(image_files) * frame_duration
                        percent = min(int((current_seconds / total_seconds) * 100), 100)
                        if percent > last_percent:
                            pbar.update(percent - last_percent)
                            last_percent = percent
                    except:
                        continue

        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {process.stderr.read()}")

    finally:
        # Clean up temporary files
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def create_video_fallback(image_files, output_path, frame_duration, resize=None):
    """
    Fallback method using OpenCV if FFmpeg is not available.
    """
    if not image_files:
        raise ValueError("No images provided")

    # Read first image to get dimensions
    with Image.open(image_files[0]) as img:
        if resize:
            img = img.resize(resize, Image.Resampling.LANCZOS)
        width, height = img.size

    # Use fixed FPS
    fps = 30
    # Calculate how many duplicate frames for each image
    frames_per_image = int(frame_duration * fps)

    # Use MJPG codec
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    video_writer = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height),
        isColor=True
    )

    if not video_writer.isOpened():
        raise RuntimeError("Failed to initialize video writer. Try a different resolution.")

    try:
        total_frames = len(image_files) * frames_per_image
        with tqdm(total=total_frames, desc="Creating video", unit="frame") as pbar:
            for image_path in image_files:
                # Use PIL for better image handling
                with Image.open(image_path) as img:
                    # Convert to RGB mode to ensure consistency
                    img = img.convert('RGB')
                    if resize:
                        img = img.resize(resize, Image.Resampling.LANCZOS)
                    
                    # Convert PIL image to OpenCV format
                    frame = np.array(img)
                    # Convert RGB to BGR format for OpenCV
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # Write the frame multiple times to achieve desired duration
                    for _ in range(frames_per_image):
                        video_writer.write(frame)
                        pbar.update(1)

    finally:
        video_writer.release()

def main():
    print("✨ Welcome to SnapMotion Wizard! ✨")
    print("Turn your 📸 photos into stunning timelapse videos in just a few steps!")

    # Step 1: Get the image folder
    image_folder = input("📂 Please enter the path to the folder with your images: ").strip()
    if not os.path.isdir(image_folder):
        print("❌ Error: The specified folder does not exist!")
        return

    # Step 2: Sorting order
    print("\n📑 How should we sort the images?")
    print("1️⃣ By filename (default)")
    print("2️⃣ By date/time")
    sort_choice = input("Enter your choice (1 or 2): ").strip() or "1"

    # Step 3: Frame duration
    duration_input = input("\n⏱️ How long should each photo be shown? (in seconds, e.g., 2.0 for two seconds): ").strip()
    try:
        frame_duration = float(duration_input) if duration_input else 2.0
        if frame_duration <= 0:
            raise ValueError
    except ValueError:
        print("❌ Error: Please enter a valid positive number!")
        return

    # Step 4: Resize option
    print("\n📏 Recommended video resolutions:")
    print("- HD (1280x720) - Good balance of quality and file size")
    print("- Full HD (1920x1080) - Higher quality, larger file")
    
    resize_choice = input(
        "\nEnter the resolution (e.g., 1280x720) or press Enter to keep original size: "
    ).strip()
    
    resize = None
    if resize_choice:
        try:
            width, height = map(int, resize_choice.split('x'))
            resize = (width, height)
        except ValueError:
            print("❌ Error: Invalid size format. Use 'widthxheight' (e.g., 1280x720).")
            return

    # Step 5: Output file details
    file_name = input("\n🖋️ Enter the desired name for the video file (without extension): ").strip()
    if not file_name:
        print("❌ Error: File name cannot be empty!")
        return

    output_folder = input("📂 Enter the folder path where the video should be saved: ").strip()
    if not os.path.isdir(output_folder):
        print("❌ Error: The specified folder does not exist!")
        return

    output_path = os.path.join(output_folder, f"{file_name}.mp4")

    # Collect and sort images
    print("\n📥 Collecting your images...")
    global image_files  # Make it accessible to create_video_with_ffmpeg
    image_files = [
        os.path.join(image_folder, f) for f in os.listdir(image_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    
    if not image_files:
        print("❌ Error: No image files found in the folder!")
        return

    if sort_choice == "2":
        image_files.sort(key=lambda x: os.path.getmtime(x))
    else:
        image_files.sort()

    # Show total number of images and estimated duration
    total_duration = len(image_files) * frame_duration
    print(f"\n📊 Summary:")
    print(f"- Total images: {len(image_files)}")
    print(f"- Duration per image: {frame_duration} seconds")
    print(f"- Estimated video duration: {total_duration:.1f} seconds")

    # Confirm and start processing
    start_process = input("\n✅ Ready to begin processing? (y/n): ").strip().lower()
    if start_process != "y":
        print("🛑 Processing canceled. Goodbye!")
        return

    try:
        # Try FFmpeg first, fall back to OpenCV if FFmpeg fails
        try:
            final_output = create_video_with_ffmpeg(image_files, output_path, frame_duration, resize)
        except Exception as e:
            print(f"\n⚠️ FFmpeg method failed, falling back to OpenCV: {str(e)}")
            final_output = create_video_fallback(image_files, output_path, frame_duration, resize)

        print(f"\n🌟 Success! Your video has been created:")
        print(f"📍 Location: {final_output}")
        print(f"⏱️ Duration: {total_duration:.1f} seconds")
        print(f"🖼️ Total frames: {len(image_files)}")
        
        # Show file size
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"📦 File size: {size_mb:.1f} MB")
        
    except Exception as e:
        print(f"\n❌ Error during video creation: {str(e)}")
        return

if __name__ == "__main__":
    main()