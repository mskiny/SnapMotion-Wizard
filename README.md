# SnapMotion Wizard 🎬

Create beautiful timelapses from your photos with ease! SnapMotion Wizard is a Python-based tool that guides you through creating professional-looking timelapse videos from your image sequences.

## Features ✨

- Easy-to-use interactive interface
- Sort images by filename or date/time
- Customizable frame duration for perfect pacing
- Support for common video resolutions
- Real-time progress tracking
- Creates high-quality MP4 videos

## Quick Setup 🚀

1. Make sure you have Python 3.7+ installed
2. Clone this repository:
   ```bash
   git clone https://github.com/mskiny/snapmotion-wizard.git
   cd snapmotion-wizard
   ```

3. Create and activate a virtual environment (recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Tool 🎯

1. Put all your images in a single folder
2. Run the script:
   ```bash
   python snapmotion_wizard.py
   ```

3. Follow the prompts:
   - Enter the path to your images folder
   - Choose sorting method (by name or date)
   - Set duration per frame (default: 0.5 seconds for timelapse effect)
   - Choose video resolution (e.g., 1280x720)
   - Set output location

## Recommended Settings 🎮

- **For Construction/Progress Timelapses:**
  - Duration: 0.5 seconds per image
  - Resolution: 1920x1080
  - Sort by date

- **For Nature/Landscape Timelapses:**
  - Duration: 0.3-0.5 seconds per image
  - Resolution: 1920x1080
  - Sort by filename

## Supported Formats 📸

- Input: JPG, JPEG, PNG
- Output: MP4 video

## Requirements 📋

- Python 3.7 or higher
- Required packages (automatically installed):
  - opencv-python
  - tqdm
  - Pillow

## Troubleshooting 🔧

If you encounter issues:
1. Ensure all requirements are installed
2. Check that your images are in supported formats
3. Try using a lower resolution if processing is slow
4. Make sure you have enough disk space

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.