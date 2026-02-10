from flask import Flask, Response, render_template, jsonify, send_from_directory, make_response, request
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TURNTABLE_IP, FLASK_HOST, FLASK_PORT, PHOTOS_BASE_DIR, STATIC_PHOTOS_DIR, ENABLE_TURNTABLE
import subprocess
import datetime
import time
import glob
import shutil
import json
import requests
from PIL import Image  # Pillow for image resizing

app = Flask(__name__)

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
BASE_PHOTO_DIR = PHOTOS_BASE_DIR  # From config.py  # adjust to your setup
current_folder_path = os.path.join(BASE_PHOTO_DIR, "default")  # fallback folder

# Turntable ESP32 configuration
# TURNTABLE_IP imported from config.py
TURNTABLE_ENABLED = ENABLE_TURNTABLE  # From config.py  # Set to False to disable turntable features

# Global variables for live preview settings
current_focus_position = "0.0"  # default to infinity/auto
current_exposure_mode = "auto"
current_shutter_speed = None
current_iso = None
current_wb_gains = None  # Format: (r_gain, b_gain) or None for auto
current_saturation = None  # -100 to 100, None for auto (maps to 0.0-2.0 for rpicam)
current_contrast = None  # -100 to 100, None for auto (maps to 0.0-2.0 for rpicam)

# Dual camera configuration
current_camera = "hq"  # "hq" (IMX477) or "v3" (IMX708)
camera_ports = {"hq": 1, "v3": 0}  # Will be updated by detect_cameras()
auto_switch_enabled = True  # Auto-switch to V3 when HQ is recording


# ---------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------
def detect_cameras():
    """
    Detect available cameras and their CSI port assignments.
    Parses output of rpicam-hello --list-cameras to find:
    - imx477 (HQ camera with 16mm lens)
    - imx708 (Camera Module V3)
    """
    global camera_ports

    try:
        result = subprocess.run(
            ["rpicam-hello", "--list-cameras"],
            capture_output=True, text=True, timeout=10
        )
        output = result.stderr + result.stdout  # libcamera outputs to stderr

        # Parse camera indices
        # Example output:
        # 0 : imx477 [4056x3040] ...
        # 1 : imx708 [4608x2592] ...

        lines = output.split('\n')
        for line in lines:
            line_lower = line.lower()
            # Look for camera index at start of line
            if line.strip() and line.strip()[0].isdigit() and ':' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    idx = int(parts[0].strip())
                    camera_info = parts[1].lower()

                    if 'imx477' in camera_info:
                        camera_ports['hq'] = idx
                        print(f"Detected HQ camera (IMX477) on port {idx}")
                    elif 'imx708' in camera_info:
                        camera_ports['v3'] = idx
                        print(f"Detected V3 camera (IMX708) on port {idx}")

        print(f"Camera ports configured: {camera_ports}")

    except subprocess.TimeoutExpired:
        print("Camera detection timeout - using defaults")
    except Exception as e:
        print(f"Camera detection error: {e} - using defaults")


def start_backup_stream():
    """Start V3 camera stream as backup while HQ is recording."""
    global current_camera
    if auto_switch_enabled and current_camera == "hq":
        current_camera = "v3"
        print("Auto-switched to V3 for preview during recording")


def restore_primary_stream():
    """Restore HQ camera stream after recording completes."""
    global current_camera
    if auto_switch_enabled and current_camera == "v3":
        current_camera = "hq"
        print("Auto-switched back to HQ after recording")
def slider_to_rpicam_value(slider_val):
    """
    Convert slider value (-100 to 100) to rpicam value (0.0 to 2.0).
    -100 = 0.0 (minimum)
    0 = 1.0 (default)
    100 = 2.0 (maximum)
    """
    return 1.0 + (slider_val / 100.0)


# ---------------------------------------------------------------------
# MJPEG Video Stream
# ---------------------------------------------------------------------
def generate_mjpeg():
    """Generate MJPEG stream from rpicam-vid."""
    global current_focus_position, current_exposure_mode, current_shutter_speed, current_iso, current_wb_gains, current_saturation, current_contrast, current_camera

    camera_id = camera_ports.get(current_camera, 0)
    print(f"Starting MJPEG stream generation on camera {current_camera} (port {camera_id})")

    # Set resolution based on camera aspect ratio
    if current_camera == "hq":
        # HQ camera (IMX477) is 4:3 aspect ratio
        width, height = "1440", "1080"
    else:
        # V3 camera (IMX708) is 16:9 aspect ratio
        width, height = "1920", "1080"

    cmd = [
        "rpicam-vid",
        "--camera", str(camera_id),
        "-t", "0",
        "--width", width,
        "--height", height,
        "--framerate", "25",
        "--codec", "mjpeg",
        "--nopreview",
        "-o", "-"
    ]

    # Only use viewfinder-mode for HQ camera (IMX477 has higher resolution sensor)
    if current_camera == "hq":
        cmd += ["--viewfinder-mode", "4056:3040"]

    # Apply custom WB gains if set
    if current_wb_gains is not None:
        r_gain, b_gain = current_wb_gains
        cmd += ["--awbgains", f"{r_gain},{b_gain}"]
        print(f"Applying WB gains: R={r_gain}, B={b_gain}")

    # Apply custom saturation if set
    if current_saturation is not None:
        sat_value = slider_to_rpicam_value(current_saturation)
        cmd += ["--saturation", str(sat_value)]
        print(f"Applying saturation: {current_saturation} -> {sat_value}")

    # Apply custom contrast if set
    if current_contrast is not None:
        contrast_value = slider_to_rpicam_value(current_contrast)
        cmd += ["--contrast", str(contrast_value)]
        print(f"Applying contrast: {current_contrast} -> {contrast_value}")

    # Apply focus lens position if set (0.0 = auto/infinity, >0 = manual distance)
    if current_focus_position is not None and current_focus_position != "0.0":
        cmd += ["--lens-position", str(current_focus_position)]
        print(f"Applying focus lens position: {current_focus_position}")

    # Apply manual exposure settings to live stream for WYSIWYG preview
    if current_exposure_mode == 'manual':
        if current_shutter_speed:
            cmd += ["--shutter", str(current_shutter_speed)]
            print(f"Applying shutter to preview: {current_shutter_speed}µs")
        if current_iso:
            gain = int(current_iso) / 100.0
            cmd += ["--gain", str(gain)]
            print(f"Applying ISO to preview: {current_iso} (gain={gain})")

    print(f"Running command: {' '.join(cmd)}")  # Debug log

    # Note: Manual exposure settings NOW apply to live stream for WYSIWYG preview
    # This matches the behavior of focus, WB, saturation, and contrast
    # All manual settings are consistently applied to both preview and capture

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(f"Failed to start rpicam-vid: {e}")
        return
        
    buffer = b""

    try:
        while True:
            data = process.stdout.read(4096)
            if not data:
                break
            buffer += data

            start = buffer.find(b'\xff\xd8')
            end = buffer.find(b'\xff\xd9')

            if start != -1 and end != -1 and end > start:
                frame = buffer[start:end + 2]
                buffer = buffer[end + 2:]
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
    except Exception as e:
        print(f"Stream error: {e}")
    finally:
        process.terminate()
        print("MJPEG stream terminated")


# ---------------------------------------------------------------------
# Flask Routes
# ---------------------------------------------------------------------
@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """MJPEG live video feed."""
    print("Video feed requested")  # Debug log
    try:
        return Response(generate_mjpeg(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Video feed error: {e}")
        return str(e), 500


# ---------------------------------------------------------------------
# Helper Function: Image Resizing
# ---------------------------------------------------------------------
def resize_image(source_path, target_path, target_size):
    """
    Resize image so its smallest side = target_size (preserving aspect ratio).
    """
    with Image.open(source_path) as img:
        w, h = img.size
        if w < h:
            scale = target_size / w
        else:
            scale = target_size / h

        new_size = (int(w * scale), int(h * scale))
        img = img.resize(new_size, Image.LANCZOS)
        img.save(target_path, quality=85, optimize=True)


# ---------------------------------------------------------------------
# Capture Photo
# ---------------------------------------------------------------------
@app.route('/capture_photo')
def capture_photo():
    """
    Capture a photo (JPEG, RAW, or both) using rpicam-still,
    save it in the selected destination folder, and generate previews.
    """

    try:
        BASE_PHOTO_DIR = PHOTOS_BASE_DIR  # From config.py
        current_folder_file = "/home/yourusername/Pictures/current_folder.txt"

        # --- Load destination folder ---
        dest_folder = os.path.join(BASE_PHOTO_DIR, "default")
        if os.path.exists(current_folder_file):
            with open(current_folder_file) as f:
                saved = f.read().strip()
                if saved:
                    dest_folder = saved
        os.makedirs(dest_folder, exist_ok=True)

        # --- Filename setup ---
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"photo_{timestamp}"

        # --- Stop stream to free the camera ---
        subprocess.run(["pkill", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        time.sleep(1)

        # --- Capture settings ---
        mode = request.args.get("mode", "auto")
        exposure_time = request.args.get("exposure_time")
        iso = request.args.get("iso")
        fmt = request.args.get("format", "jpeg").lower()
        hdr_mode = request.args.get("hdr_mode", "normal")
        ev = request.args.get("ev", "0")

        jpeg_path = os.path.join(dest_folder, f"{base_filename}.jpg")
        raw_path = os.path.join(dest_folder, f"{base_filename}.dng")

        # --- Build libcamera command ---
        camera_id = camera_ports.get(current_camera, 0)
        cmd = ["rpicam-still", "--camera", str(camera_id), "-t", "10", "--nopreview"]
        print(f"Capturing with camera {current_camera} (port {camera_id})")

        # --- HDR mode settings ---
        if hdr_mode == "hdr":
            # Enable true HDR mode (Camera Module V3)
            cmd += ["--hdr"]
            # Apply EV compensation with HDR
            try:
                # Convert EV string to float (e.g., "+1.5" -> 1.5, "-2" -> -2.0)
                ev_val = float(ev.replace('+', ''))
                # rpicam-still accepts EV as a plain number (positive or negative)
                cmd += ["--ev", str(ev_val)]
                print(f"Applying EV compensation: {ev_val}")
            except ValueError:
                print(f"Invalid EV value: {ev}")
                pass

            # WARNING: HDR requires auto exposure for proper bracketing
            # Manual exposure (shutter/ISO) will be ignored in HDR mode
            print("HDR mode enabled - using auto exposure for bracketing")

        # --- Manual Exposure (only if NOT in HDR mode) ---
        elif mode == "manual":
            if exposure_time:
                cmd += ["--shutter", str(exposure_time)]
                print(f"Applying manual shutter: {exposure_time}µs")
            if iso:
                # Convert ISO to gain
                try:
                    iso_val = int(iso)
                    gain = iso_val / 100.0
                    cmd += ["--gain", str(gain)]
                    print(f"Applying manual ISO: {iso_val} (gain={gain})")
                except ValueError:
                    pass

        # --- Focus settings ---
        focus_mode = request.args.get("focus_mode", "auto")
        focus_distance = request.args.get("focus_distance")

        if focus_mode == "manual" and focus_distance:
            cmd += ["--lens-position", focus_distance]

        # --- White Balance settings ---
        if current_wb_gains is not None:
            r_gain, b_gain = current_wb_gains
            cmd += ["--awbgains", f"{r_gain},{b_gain}"]
            print(f"Applying WB to photo capture: R={r_gain}, B={b_gain}")

        # --- Saturation settings ---
        if current_saturation is not None:
            sat_value = slider_to_rpicam_value(current_saturation)
            cmd += ["--saturation", str(sat_value)]
            print(f"Applying saturation to photo: {current_saturation} -> {sat_value}")

        # --- Contrast settings ---
        if current_contrast is not None:
            contrast_value = slider_to_rpicam_value(current_contrast)
            cmd += ["--contrast", str(contrast_value)]
            print(f"Applying contrast to photo: {current_contrast} -> {contrast_value}")

        # --- Format handling ---
        if fmt == "jpeg":
            cmd += ["-o", jpeg_path]
        elif fmt == "raw":
            cmd += ["-o", raw_path, "--raw"]
        elif fmt == "both":
            cmd += ["-o", jpeg_path, "--raw"]
        else:
            return jsonify({"error": "Invalid format"}), 400

        print("Running capture:", " ".join(cmd))
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            return jsonify({
                "error": "Capture failed",
                "stderr": result.stderr.decode()
            }), 500

        # --- No preview/thumbnail generation (changed workflow) ---
        # Images will be processed later via Digikam for web versions

        # --- Response ---
        response = {
            "message": f"Photo saved ({fmt})",
            "folder": os.path.basename(dest_folder),
        }
        if fmt in ("jpeg", "both"):
            response["jpeg_file"] = os.path.basename(jpeg_path)
        if fmt in ("raw", "both"):
            response["raw_file"] = os.path.basename(raw_path)

        return jsonify(response)

    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------
# Serve and List Photos
# ---------------------------------------------------------------------
@app.route('/photos/<path:filename>')
def serve_photo(filename):
    # Get current folder (read from file for most up-to-date path)
    current_folder_file = "/home/yourusername/Pictures/current_folder.txt"
    folder_path = os.path.join(BASE_PHOTO_DIR, "default")
    if os.path.exists(current_folder_file):
        with open(current_folder_file) as f:
            saved = f.read().strip()
            if saved:
                folder_path = saved

    response = send_from_directory(folder_path, filename)
    response.cache_control.max_age = 3600  # cache for 1 hour
    return response

recent_photos_cache = {
    "photos": [],
    "last_updated": 0
}

@app.route('/recent_photos')
def recent_photos():
    """Return JSON list of 5 most recent photos (excluding thumbs/previews)."""
    global recent_photos_cache
    cache_duration = 5  # Cache results for 5 seconds

    # Use cached results if they are still valid
    if time.time() - recent_photos_cache["last_updated"] < cache_duration:
        return jsonify(recent_photos_cache["photos"])

    # Get current folder (read from file for most up-to-date path)
    current_folder_file = "/home/yourusername/Pictures/current_folder.txt"
    folder_path = os.path.join(BASE_PHOTO_DIR, "default")
    if os.path.exists(current_folder_file):
        with open(current_folder_file) as f:
            saved = f.read().strip()
            if saved:
                folder_path = saved

    # Fetch photos from main folder
    photos = glob.glob(os.path.join(folder_path, "photo_*.jpg"))

    # Also fetch photos from 360° sequence subfolders
    seq_folders = glob.glob(os.path.join(folder_path, "360seq_*"))
    for seq_folder in seq_folders:
        photos.extend(glob.glob(os.path.join(seq_folder, "photo_*.jpg")))

    # Sort by modification time and filter
    photos = sorted(photos, key=os.path.getmtime, reverse=True)
    photos = [p for p in photos if not ("_preview" in p or "_thumb" in p)]

    # Return relative paths for photos in subfolders
    filenames = []
    for p in photos[:5]:
        rel_path = os.path.relpath(p, folder_path)
        filenames.append(rel_path)

    # Update cache
    recent_photos_cache["photos"] = filenames
    recent_photos_cache["last_updated"] = time.time()

    return jsonify(filenames)

@app.route('/last_modified')
def last_modified():
    """Return the last modified time of the index.html file."""
    index_path = os.path.join(app.template_folder, 'index.html')
    if os.path.exists(index_path):
        last_modified_time = os.path.getmtime(index_path)
        return jsonify({
            'last_modified': last_modified_time
        })
    return jsonify({'error': 'File not found'}), 404

# ---------------------------------------------------------------------
# Set Focus Position (live preview)
# ---------------------------------------------------------------------
@app.route('/set_focus', methods=['POST'])
def set_focus():
    """Update focus position and restart video stream."""
    global current_focus_position
    
    focus_distance = request.form.get('focus_distance', '0.0')
    current_focus_position = focus_distance
    
    # Kill existing stream to restart with new focus
    subprocess.run(["pkill", "-9", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    
    return jsonify({"message": "Focus updated", "focus_position": current_focus_position})

# ---------------------------------------------------------------------
# Set Exposure Settings (live preview)
# ---------------------------------------------------------------------
@app.route('/set_exposure', methods=['POST'])
def set_exposure():
    """Update exposure settings and restart video stream."""
    global current_exposure_mode, current_shutter_speed, current_iso
    
    current_exposure_mode = request.form.get('mode', 'auto')
    current_shutter_speed = request.form.get('shutter_speed')
    current_iso = request.form.get('iso')
    
    # Kill existing stream to restart with new exposure
    subprocess.run(["pkill", "-9", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    
    return jsonify({
        "message": "Exposure updated",
        "mode": current_exposure_mode,
        "shutter": current_shutter_speed,
        "iso": current_iso
    })

# ---------------------------------------------------------------------
# Restart Video Stream (recovery endpoint)
# ---------------------------------------------------------------------
@app.route('/restart_stream', methods=['POST'])
def restart_stream():
    """Force restart the video stream."""
    subprocess.run(["pkill", "-9", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    return jsonify({"message": "Stream restarted"})

# ---------------------------------------------------------------------
# Apply White Balance (from temp/tint)
# ---------------------------------------------------------------------
@app.route('/apply_wb', methods=['POST'])
def apply_wb():
    """Apply white balance using temperature and tint values."""
    global current_wb_gains

    try:
        temp = float(request.form.get('temp', 5500))
        tint = float(request.form.get('tint', 0))
        r_gain = float(request.form.get('r_gain', 1.0))
        b_gain = float(request.form.get('b_gain', 1.0))

        # Store gains globally
        current_wb_gains = (r_gain, b_gain)

        # Kill existing stream to restart with new WB
        subprocess.run(["pkill", "-9", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        time.sleep(0.5)

        print(f"WB applied: {temp}K, Tint: {tint} → R={r_gain:.2f}, B={b_gain:.2f}")

        return jsonify({
            "message": "WB applied successfully",
            "temp": temp,
            "tint": tint,
            "r_gain": r_gain,
            "b_gain": b_gain
        })

    except Exception as e:
        print(f"WB apply error: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------
# White Balance Sampling (returns RGB values)
# ---------------------------------------------------------------------
@app.route('/sample_wb', methods=['POST'])
def sample_wb():
    """Sample white balance from a clicked point in the live preview."""
    global current_wb_gains

    try:
        # Get click coordinates
        x = int(request.form.get('x', 0))
        y = int(request.form.get('y', 0))
        image_width = int(request.form.get('image_width', 1920))
        image_height = int(request.form.get('image_height', 1080))

        # Stop stream to free camera
        subprocess.run(["pkill", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        time.sleep(0.5)

        # Capture a still frame for sampling with neutral AWB (no auto correction)
        # Allow time for AEC (auto exposure) to stabilize, but disable AWB
        temp_path = "/tmp/wb_sample.jpg"
        camera_id = camera_ports.get(current_camera, 0)
        cmd = [
            "rpicam-still",
            "--camera", str(camera_id),
            "-t", "500",  # Give camera time to adjust exposure
            "--nopreview",
            "--width", str(image_width),
            "--height", str(image_height),
            "--awbgains", "1,1",  # Set neutral gains (integers work better)
            "-o", temp_path
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return jsonify({"error": "Failed to capture sample image"}), 500

        # Load image and sample region
        with Image.open(temp_path) as img:
            img_width, img_height = img.size

            # Define sampling region (20x20 pixels around click point)
            region_size = 20
            half_size = region_size // 2

            # Clamp coordinates to image bounds
            x1 = max(0, x - half_size)
            y1 = max(0, y - half_size)
            x2 = min(img_width, x + half_size)
            y2 = min(img_height, y + half_size)

            # Check if region is valid
            if x1 >= x2 or y1 >= y2:
                return jsonify({"error": "Sample region out of bounds"}), 400

            # Extract region and convert to RGB
            region = img.crop((x1, y1, x2, y2))
            if region.mode != 'RGB':
                region = region.convert('RGB')

            # Calculate average RGB values
            pixels = list(region.getdata())
            r_avg = sum(p[0] for p in pixels) / len(pixels)
            g_avg = sum(p[1] for p in pixels) / len(pixels)
            b_avg = sum(p[2] for p in pixels) / len(pixels)

            # Log RGB values for debugging
            print(f"Sampled RGB values: R={r_avg:.1f}, G={g_avg:.1f}, B={b_avg:.1f}")

            # Validate sample (more permissive thresholds)
            avg_brightness = (r_avg + g_avg + b_avg) / 3
            print(f"Average brightness: {avg_brightness:.1f}")

            if avg_brightness < 10:
                return jsonify({"error": "Sample too dark, choose brighter area"}), 400

            if avg_brightness > 245:
                return jsonify({"error": "Sample too bright, choose darker area"}), 400

        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass

        # Return RGB averages (frontend will convert to temp/tint)
        return jsonify({
            "message": "WB sampled successfully",
            "r_avg": round(r_avg, 2),
            "g_avg": round(g_avg, 2),
            "b_avg": round(b_avg, 2)
        })

    except Exception as e:
        print(f"WB sampling error: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------
# Reset White Balance
# ---------------------------------------------------------------------
@app.route('/reset_wb', methods=['POST'])
def reset_wb():
    """Reset white balance to auto."""
    global current_wb_gains

    try:
        current_wb_gains = None

        # Kill existing stream to restart with auto WB
        subprocess.run(["pkill", "-9", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        time.sleep(0.5)

        print("WB reset to auto")

        return jsonify({"message": "WB reset to auto"})

    except Exception as e:
        print(f"WB reset error: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------
# Apply Saturation
# ---------------------------------------------------------------------
@app.route('/apply_saturation', methods=['POST'])
def apply_saturation():
    """Apply saturation setting."""
    global current_saturation

    try:
        saturation = int(request.form.get('saturation', 0))
        current_saturation = saturation

        # Kill existing stream to restart with new saturation
        subprocess.run(["pkill", "-9", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        time.sleep(0.5)

        print(f"Saturation applied: {saturation}")

        return jsonify({
            "message": "Saturation applied successfully",
            "saturation": saturation
        })

    except Exception as e:
        print(f"Saturation apply error: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------
# Reset Saturation
# ---------------------------------------------------------------------
@app.route('/reset_saturation', methods=['POST'])
def reset_saturation():
    """Reset saturation to auto."""
    global current_saturation

    try:
        current_saturation = None

        # Kill existing stream to restart with auto saturation
        subprocess.run(["pkill", "-9", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        time.sleep(0.5)

        print("Saturation reset to auto")

        return jsonify({"message": "Saturation reset to auto"})

    except Exception as e:
        print(f"Saturation reset error: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------
# Apply Contrast
# ---------------------------------------------------------------------
@app.route('/apply_contrast', methods=['POST'])
def apply_contrast():
    """Apply contrast setting."""
    global current_contrast

    try:
        contrast = int(request.form.get('contrast', 0))
        current_contrast = contrast

        # Kill existing stream to restart with new contrast
        subprocess.run(["pkill", "-9", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        time.sleep(0.5)

        print(f"Contrast applied: {contrast}")

        return jsonify({
            "message": "Contrast applied successfully",
            "contrast": contrast
        })

    except Exception as e:
        print(f"Contrast apply error: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------
# Reset Contrast
# ---------------------------------------------------------------------
@app.route('/reset_contrast', methods=['POST'])
def reset_contrast():
    """Reset contrast to auto."""
    global current_contrast

    try:
        current_contrast = None

        # Kill existing stream to restart with auto contrast
        subprocess.run(["pkill", "-9", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        time.sleep(0.5)

        print("Contrast reset to auto")

        return jsonify({"message": "Contrast reset to auto"})

    except Exception as e:
        print(f"Contrast reset error: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------
# Restart Application
# ---------------------------------------------------------------------
@app.route('/restart_app', methods=['POST'])
def restart_app():
    """Restart the Flask application."""
    import sys
    subprocess.run(["pkill", "-9", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
    subprocess.Popen([sys.executable] + sys.argv)
    return jsonify({"message": "Application restarting..."})
    # Note: The current process will exit after this response

# ---------------------------------------------------------------------
# Kill Camera Processes (Emergency Stop)
# ---------------------------------------------------------------------
@app.route('/kill_camera_processes', methods=['POST'])
def kill_camera_processes():
    """Kill all running camera processes (rpicam-vid, rpicam-still)."""
    try:
        # Kill rpicam-vid (live stream)
        subprocess.run(["pkill", "-9", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        # Kill rpicam-still (photo capture)
        subprocess.run(["pkill", "-9", "-f", "rpicam-still"], stderr=subprocess.DEVNULL)
        # Kill ffmpeg (video conversion)
        subprocess.run(["pkill", "-9", "-f", "ffmpeg"], stderr=subprocess.DEVNULL)

        print("Emergency stop: All camera processes killed")
        time.sleep(0.5)  # Give processes time to die

        return jsonify({"message": "Camera processes killed", "status": "success"})
    except Exception as e:
        print(f"Error killing camera processes: {e}")
        return jsonify({"error": str(e), "status": "error"}), 500

# ---------------------------------------------------------------------
# Video recording
#----------------------------------------------------------------------
@app.route('/record_video', methods=['POST'])
def record_video():
    """
    Record a video with the Pi camera for a given duration (seconds).
    Uses HQ camera for recording, auto-switches to V3 for preview if enabled.
    """
    try:
        duration = int(request.form.get("duration", 10))  # default 10s
        folder = current_folder_path
        os.makedirs(folder, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        h264_path = os.path.join(folder, f"video_{timestamp}.h264")
        mp4_path = os.path.join(folder, f"video_{timestamp}.mp4")

        # --- Stop live feed to free HQ camera ---
        subprocess.run(["pkill", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        time.sleep(1)

        # --- Auto-switch to V3 for preview during recording ---
        start_backup_stream()

        # --- Record video with HQ camera (always use HQ for recording) ---
        hq_camera_id = camera_ports.get("hq", 0)
        cmd = [
            "rpicam-vid",
            "--camera", str(hq_camera_id),
            "--width", "1920",
            "--height", "1080",
            "-t", str(duration * 1000),  # duration in milliseconds
            "--codec", "h264",
            "-o", h264_path
        ]
        print(f"Recording video with HQ camera (port {hq_camera_id})")

        # --- Apply White Balance settings ---
        if current_wb_gains is not None:
            r_gain, b_gain = current_wb_gains
            cmd += ["--awbgains", f"{r_gain},{b_gain}"]
            print(f"Applying WB to video recording: R={r_gain}, B={b_gain}")

        # --- Apply Saturation settings ---
        if current_saturation is not None:
            sat_value = slider_to_rpicam_value(current_saturation)
            cmd += ["--saturation", str(sat_value)]
            print(f"Applying saturation to video: {current_saturation} -> {sat_value}")

        # --- Apply Contrast settings ---
        if current_contrast is not None:
            contrast_value = slider_to_rpicam_value(current_contrast)
            cmd += ["--contrast", str(contrast_value)]
            print(f"Applying contrast to video: {current_contrast} -> {contrast_value}")

        print("Recording video:", " ".join(cmd))
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            return jsonify({"error": "Recording failed", "stderr": result.stderr.decode()}), 500

        # --- Convert to MP4 ---
        cmd_mp4 = [
            "ffmpeg",
            "-y",  # overwrite if exists
            "-framerate", "30",
            "-i", h264_path,
            "-c", "copy",
            mp4_path
        ]
        result_mp4 = subprocess.run(cmd_mp4, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result_mp4.returncode != 0:
            return jsonify({"error": "MP4 conversion failed", "stderr": result_mp4.stderr.decode()}), 500

        # --- Delete .h264 after successful conversion ---
        if os.path.exists(mp4_path):
            try:
                os.remove(h264_path)
            except Exception as e:
                print(f"Warning: could not delete {h264_path}: {e}")

        # --- Restore HQ camera for preview ---
        restore_primary_stream()

        return jsonify({
            "message": "Video recorded successfully",
            "mp4": os.path.basename(mp4_path)
        })

    except Exception as e:
        print("Video recording error:", e)
        # Stop turntable on error to prevent endless spinning
        turntable_request('/stop')
        restore_primary_stream()  # Ensure we restore even on error
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------
# Disk Storage Info
# ---------------------------------------------------------------------
@app.route('/storage')
def get_storage_info():
    """Return available storage in GB."""
    total, used, free = shutil.disk_usage("/")
    free_gb = round(free / (1024**3), 1)
    return jsonify(free=f"{free_gb} GB")


# ---------------------------------------------------------------------
# List Available Folders
# ---------------------------------------------------------------------
@app.route('/list_folders')
def list_folders():
    """Return list of photo folders, excluding web-ready."""
    try:
        folders = []
        for item in os.listdir(BASE_PHOTO_DIR):
            path = os.path.join(BASE_PHOTO_DIR, item)
            # Exclude web-ready folder and non-directories
            if os.path.isdir(path) and item != "web-ready":
                folders.append(item)
        # Sort by modification time, most recent first
        folders.sort(key=lambda x: os.path.getmtime(os.path.join(BASE_PHOTO_DIR, x)), reverse=True)
        return jsonify(folders)
    except Exception as e:
        return jsonify([]), 500

# ---------------------------------------------------------------------
# Set Destination folder
# ---------------------------------------------------------------------
@app.route('/set_folder', methods=['POST'])
def set_folder():
    global current_folder_path
    folder_name = request.form.get('folder', '').strip()

    # Secure + make directory
    if folder_name:
        safe_name = folder_name.replace('/', '_').replace('\\', '_')
        folder_path = os.path.join(BASE_PHOTO_DIR, safe_name)
        os.makedirs(folder_path, exist_ok=True)
        current_folder_path = folder_path
        # Optional: persist it to a text file
        with open('/home/yourusername/Pictures/current_folder.txt', 'w') as f:
            f.write(current_folder_path)
        return safe_name
    else:
        return "Invalid folder", 400


# ---------------------------------------------------------------------
# Camera Metadata - Helper Functions
# ---------------------------------------------------------------------

# IMX708 ct_curve data (from tuning file)
CT_CURVE = [
    {"temp": 2964, "inv_r": 0.7451, "inv_b": 0.3213},
    {"temp": 3610, "inv_r": 0.6119, "inv_b": 0.4443},
    {"temp": 4640, "inv_r": 0.5168, "inv_b": 0.5419},
    {"temp": 5910, "inv_r": 0.4436, "inv_b": 0.6229},
    {"temp": 7590, "inv_r": 0.3847, "inv_b": 0.6921}
]

def colour_gains_to_temp_tint(r_gain, b_gain):
    """
    Convert ColourGains (R and B) to temperature and tint using IMX708 ct_curve.
    Returns: (temperature_kelvin, tint_value)
    """
    # Convert gains to inverse gains (as stored in ct_curve)
    # Note: ct_curve stores inv_r = R/G and inv_b = B/G
    # Camera reports gains as multipliers applied to R and B channels
    inv_r = 1.0 / r_gain if r_gain > 0 else 1.0
    inv_b = 1.0 / b_gain if b_gain > 0 else 1.0

    # Calculate R/B ratio for temperature matching
    rb_ratio = inv_r / inv_b if inv_b > 0 else 1.0

    # Find closest temperature in ct_curve
    best_temp = CT_CURVE[0]["temp"]
    min_diff = float('inf')

    for entry in CT_CURVE:
        curve_rb_ratio = entry["inv_r"] / entry["inv_b"]
        diff = abs(curve_rb_ratio - rb_ratio)
        if diff < min_diff:
            min_diff = diff
            best_temp = entry["temp"]

    # For tint, compare actual inv_r/inv_b to expected values at this temperature
    # Interpolate to get expected values
    temp_kelvin = best_temp

    # Find bracketing temperatures for interpolation
    if temp_kelvin <= CT_CURVE[0]["temp"]:
        expected_inv_r = CT_CURVE[0]["inv_r"]
        expected_inv_b = CT_CURVE[0]["inv_b"]
    elif temp_kelvin >= CT_CURVE[-1]["temp"]:
        expected_inv_r = CT_CURVE[-1]["inv_r"]
        expected_inv_b = CT_CURVE[-1]["inv_b"]
    else:
        # Linear interpolation
        for i in range(len(CT_CURVE) - 1):
            if CT_CURVE[i]["temp"] <= temp_kelvin <= CT_CURVE[i+1]["temp"]:
                t1 = CT_CURVE[i]["temp"]
                t2 = CT_CURVE[i+1]["temp"]
                factor = (temp_kelvin - t1) / (t2 - t1) if t2 != t1 else 0

                expected_inv_r = CT_CURVE[i]["inv_r"] + factor * (CT_CURVE[i+1]["inv_r"] - CT_CURVE[i]["inv_r"])
                expected_inv_b = CT_CURVE[i]["inv_b"] + factor * (CT_CURVE[i+1]["inv_b"] - CT_CURVE[i]["inv_b"])
                break

    # Calculate tint from deviation
    # Green channel deviation indicates tint
    avg_deviation = ((inv_r - expected_inv_r) / expected_inv_r + (inv_b - expected_inv_b) / expected_inv_b) / 2
    tint = -avg_deviation * 50  # Scale and invert
    tint = max(-50, min(50, tint))  # Clamp to ±50

    return int(temp_kelvin), int(tint)

def microseconds_to_shutter_string(exposure_us):
    """
    Convert exposure time in microseconds to human-readable shutter speed.
    Examples: 16667 -> "1/60", 1000000 -> "1s"
    """
    if exposure_us <= 0:
        return "0"

    exposure_s = exposure_us / 1_000_000

    # If less than 1 second, express as fraction
    if exposure_s < 1:
        denominator = int(1 / exposure_s)
        return f"1/{denominator}"
    else:
        # Round to 1 decimal place
        return f"{exposure_s:.1f}s"

# ---------------------------------------------------------------------
# Camera Metadata Endpoint
# ---------------------------------------------------------------------
@app.route('/camera_metadata')
def camera_metadata():
    """
    Capture current camera metadata (ISO, shutter, WB, tint) using rpicam-still.
    Returns JSON with formatted camera settings.
    """
    try:
        # Kill rpicam-vid to free camera (it will restart automatically)
        subprocess.run(["pkill", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        time.sleep(0.15)  # Minimal pause to ensure camera is freed

        # Capture metadata without saving image
        camera_id = camera_ports.get(current_camera, 0)
        cmd = [
            "rpicam-still",
            "--camera", str(camera_id),
            "--metadata", "-",
            "--metadata-format", "json",
            "--immediate",
            "--nopreview",
            "-o", "/dev/null"
        ]

        # Apply current manual settings if in manual mode
        if current_exposure_mode == 'manual':
            if current_shutter_speed:
                cmd += ["--shutter", str(current_shutter_speed)]
            if current_iso:
                gain = int(current_iso) / 100.0
                cmd += ["--gain", str(gain)]

        # Apply current WB if set
        if current_wb_gains is not None:
            r_gain, b_gain = current_wb_gains
            cmd += ["--awbgains", f"{r_gain},{b_gain}"]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        if result.returncode != 0:
            return jsonify({"error": "Failed to capture metadata"}), 500

        # Parse JSON metadata
        metadata = json.loads(result.stdout)

        # Extract values
        exposure_time = metadata.get("ExposureTime", 0)  # in microseconds
        analogue_gain = metadata.get("AnalogueGain", 1.0)
        colour_gains = metadata.get("ColourGains", [1.0, 1.0])  # [R, B]

        # Convert to user-friendly format
        iso = int(analogue_gain * 100)
        shutter_speed = microseconds_to_shutter_string(exposure_time)

        # Extract R and B gains
        r_gain = colour_gains[0] if len(colour_gains) > 0 else 1.0
        b_gain = colour_gains[1] if len(colour_gains) > 1 else 1.0

        # Convert to temperature and tint
        wb_temp, wb_tint = colour_gains_to_temp_tint(r_gain, b_gain)

        return jsonify({
            "iso": iso,
            "gain": round(analogue_gain, 2),
            "shutter_speed": shutter_speed,
            "shutter_us": exposure_time,
            "wb_temp": wb_temp,
            "wb_tint": wb_tint,
            "wb_r_gain": round(r_gain, 2),
            "wb_b_gain": round(b_gain, 2),
            "timestamp": int(time.time() * 1000)  # milliseconds
        })

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Metadata capture timeout"}), 500
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Output was: {result.stdout}")
        return jsonify({"error": "Failed to parse metadata"}), 500
    except Exception as e:
        print(f"Metadata error: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------
# Turntable Control Endpoints
# ---------------------------------------------------------------------

def turntable_request(endpoint, method='POST', params=None):
    """Helper function to send requests to ESP32 turntable."""
    if not TURNTABLE_ENABLED:
        return {"status": "error", "message": "Turntable disabled"}

    try:
        url = f"http://{TURNTABLE_IP}{endpoint}"
        if method == 'GET':
            response = requests.get(url, params=params, timeout=2)
        else:
            response = requests.post(url, params=params, timeout=30)

        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Turntable timeout"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Cannot connect to turntable"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def turntable_rotate_and_wait(degrees, settle_time=1.0, timeout=60):
    """
    Send rotation command and wait for completion by polling status.
    The ESP32 blocking endpoints drop the HTTP connection before responding,
    but the motor still rotates. This helper polls /status until done.
    """
    # Send rotation command (response may fail due to ESP32 blocking behavior)
    turntable_request('/rotate_degrees', params={'degrees': degrees})

    # Poll status until turntable stops moving
    poll_interval = 0.5
    waited = 0.0
    time.sleep(0.5)  # Brief delay for ESP32 to register movement

    while waited < timeout:
        status = turntable_request('/status', method='GET')
        if status.get('status') != 'error':
            if not status.get('is_moving', True) and status.get('distance_to_go', 1) == 0:
                time.sleep(settle_time)
                return {"status": "success", "message": f"Rotated {degrees} degrees"}
        time.sleep(poll_interval)
        waited += poll_interval

    return {"status": "error", "message": "Turntable rotation timeout"}


def turntable_home_and_wait(timeout=60):
    """
    Send home command and wait for completion by polling status.
    """
    turntable_request('/home')

    poll_interval = 0.5
    waited = 0.0
    time.sleep(0.5)

    while waited < timeout:
        status = turntable_request('/status', method='GET')
        if status.get('status') != 'error':
            if not status.get('is_moving', True) and status.get('distance_to_go', 1) == 0:
                time.sleep(0.5)
                return {"status": "success"}
        time.sleep(poll_interval)
        waited += poll_interval

    return {"status": "error", "message": "Turntable home timeout"}


@app.route('/turntable/status')
def turntable_status():
    """Get turntable status."""
    result = turntable_request('/status', method='GET')
    return jsonify(result)

@app.route('/turntable/left', methods=['POST'])
def turntable_left():
    """Rotate turntable left (CCW)."""
    degrees = request.form.get('degrees', 90)
    result = turntable_request('/left', params={'degrees': degrees})
    return jsonify(result)

@app.route('/turntable/right', methods=['POST'])
def turntable_right():
    """Rotate turntable right (CW)."""
    degrees = request.form.get('degrees', 90)
    result = turntable_request('/right', params={'degrees': degrees})
    return jsonify(result)

@app.route('/turntable/goto', methods=['POST'])
def turntable_goto():
    """Go to absolute position."""
    position = request.form.get('position', 0)
    result = turntable_request('/goto', params={'position': position})
    return jsonify(result)

@app.route('/turntable/home', methods=['POST'])
def turntable_home():
    """Return to home position."""
    result = turntable_request('/home')
    return jsonify(result)

@app.route('/turntable/set_home', methods=['POST'])
def turntable_set_home():
    """Set current position as home."""
    result = turntable_request('/set_home')
    return jsonify(result)

@app.route('/turntable/stop', methods=['POST'])
def turntable_stop():
    """Emergency stop."""
    result = turntable_request('/stop')
    return jsonify(result)

# ---------------------------------------------------------------------
# 360° Photo Sequence Capture
# ---------------------------------------------------------------------
@app.route('/capture_360_sequence', methods=['POST'])
def capture_360_sequence():
    """
    Capture a sequence of photos while rotating 360°.
    Parameters:
    - photo_count: Number of photos to capture (default: 36, i.e., every 10°)
    - format: jpeg, raw, or both (default: jpeg)
    """
    try:
        photo_count = int(request.form.get('photo_count', 36))
        fmt = request.form.get('format', 'jpeg').lower()

        if photo_count < 1 or photo_count > 360:
            return jsonify({"error": "Invalid photo count (1-360)"}), 400

        # Prepare turntable for 360° sequence
        turntable_info = turntable_request('/photo360', params={'count': photo_count})
        if turntable_info.get('status') == 'error':
            return jsonify(turntable_info), 500

        degrees_per_photo = turntable_info.get('degrees_per_photo', 360.0 / photo_count)

        # Create subfolder for this sequence
        BASE_PHOTO_DIR = PHOTOS_BASE_DIR  # From config.py
        current_folder_file = "/home/yourusername/Pictures/current_folder.txt"

        dest_folder = os.path.join(BASE_PHOTO_DIR, "default")
        if os.path.exists(current_folder_file):
            with open(current_folder_file) as f:
                saved = f.read().strip()
                if saved:
                    dest_folder = saved

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        sequence_folder = os.path.join(dest_folder, f"360seq_{timestamp}")
        os.makedirs(sequence_folder, exist_ok=True)

        captured_files = []

        # --- Stop live feed to free camera ---
        subprocess.run(["pkill", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        time.sleep(1)

        # Return to home position first
        turntable_home_and_wait()

        for i in range(photo_count):
            # Capture photo
            photo_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"photo_{i+1:03d}_{photo_timestamp}"

            jpeg_path = os.path.join(sequence_folder, f"{base_filename}.jpg")
            raw_path = os.path.join(sequence_folder, f"{base_filename}.dng")

            # Build capture command - use HQ camera for 360 sequence
            hq_camera_id = camera_ports.get("hq", 0)
            cmd = ["rpicam-still", "--camera", str(hq_camera_id), "-t", "10", "--nopreview"]

            # Apply current camera settings
            if current_wb_gains is not None:
                r_gain, b_gain = current_wb_gains
                cmd += ["--awbgains", f"{r_gain},{b_gain}"]

            if current_saturation is not None:
                sat_value = slider_to_rpicam_value(current_saturation)
                cmd += ["--saturation", str(sat_value)]

            if current_contrast is not None:
                contrast_value = slider_to_rpicam_value(current_contrast)
                cmd += ["--contrast", str(contrast_value)]

            # Apply focus lens position if set (manual focus)
            if current_focus_position is not None and current_focus_position != "0.0":
                cmd += ["--lens-position", str(current_focus_position)]
                print(f"Applying focus: {current_focus_position}")

            # Apply manual exposure settings if in manual mode
            if current_exposure_mode == 'manual':
                if current_shutter_speed:
                    cmd += ["--shutter", str(current_shutter_speed)]
                    print(f"Applying shutter: {current_shutter_speed}µs")
                if current_iso:
                    gain = int(current_iso) / 100.0
                    cmd += ["--gain", str(gain)]
                    print(f"Applying ISO: {current_iso} (gain={gain})")

            # Format handling
            if fmt == "jpeg":
                cmd += ["-o", jpeg_path]
            elif fmt == "raw":
                cmd += ["-o", raw_path, "--raw"]
            elif fmt == "both":
                cmd += ["-o", jpeg_path, "--raw"]

            # Capture
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode != 0:
                print(f"Capture {i+1} failed: {result.stderr.decode()}")
                continue

            captured_files.append(base_filename)
            print(f"Captured {i+1}/{photo_count}")

            # Rotate to next position (except after last photo)
            if i < photo_count - 1:
                rotate_result = turntable_rotate_and_wait(degrees_per_photo)
                if rotate_result.get('status') == 'error':
                    return jsonify({
                        "error": "Turntable rotation failed",
                        "details": rotate_result
                    }), 500

        # Return to home
        turntable_home_and_wait()

        return jsonify({
            "message": f"360° sequence complete: {len(captured_files)} photos",
            "folder": sequence_folder,
            "photo_count": len(captured_files),
            "files": captured_files
        })

    except Exception as e:
        print(f"360° sequence error: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------
# 360° Video Recording
# ---------------------------------------------------------------------
@app.route('/record_360_video', methods=['POST'])
def record_360_video():
    """
    Record video while rotating 360°.
    Uses HQ camera for recording, auto-switches to V3 for preview if enabled.
    Parameters:
    - duration: Duration in seconds for full 360° rotation (default: 30)
    - loop_mode: If '1', accelerate before recording and decelerate after (for seamless loops)
    """
    try:
        duration = int(request.form.get('duration', 30))
        loop_mode = request.form.get('loop_mode', '0') == '1'

        if duration < 5 or duration > 300:
            return jsonify({"error": "Invalid duration (5-300 seconds)"}), 400

        # Prepare destination
        BASE_PHOTO_DIR = PHOTOS_BASE_DIR  # From config.py
        current_folder_file = "/home/yourusername/Pictures/current_folder.txt"

        dest_folder = os.path.join(BASE_PHOTO_DIR, "default")
        if os.path.exists(current_folder_file):
            with open(current_folder_file) as f:
                saved = f.read().strip()
                if saved:
                    dest_folder = saved

        os.makedirs(dest_folder, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        h264_path = os.path.join(dest_folder, f"video_360_{timestamp}.h264")
        mp4_path = os.path.join(dest_folder, f"video_360_{timestamp}.mp4")

        # --- Stop live feed to free HQ camera ---
        subprocess.run(["pkill", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        time.sleep(1)

        # --- Auto-switch to V3 for preview during recording ---
        start_backup_stream()

        if loop_mode:
            # Loop mode: Pre-position backwards, then accelerate forward through starting position
            # Recording starts when object reaches its original position (already at cruise speed)

            # Calculate timings
            accel_time = duration * 0.1  # Time to accelerate to cruise speed (10% of duration)
            decel_time = duration * 0.1  # Time to decelerate (same as accel)
            preposition_time = 2.0  # Time to move backwards 36° to pre-position
            return_home_time = 2.0  # Time to return to starting position after rotation

            # Start turntable in loop mode
            turntable_result = turntable_request('/video360_loop', params={'duration': duration})
            if turntable_result.get('status') == 'error':
                return jsonify(turntable_result), 500

            # Wait for: pre-positioning backwards + acceleration time
            # When this time is up, object is back at starting position and at cruise speed
            time.sleep(preposition_time + accel_time)

            # Record the constant-speed portion (80% of duration)
            # This captures full 360° rotation at constant speed
            video_duration_ms = int((duration - 2 * accel_time) * 1000)
        else:
            # Normal mode: Record entire rotation including acceleration/deceleration
            # Start turntable rotation
            turntable_result = turntable_request('/video360', params={'duration': duration})
            if turntable_result.get('status') == 'error':
                return jsonify(turntable_result), 500

            # Small delay to ensure turntable starts
            time.sleep(0.2)

            # Add buffer to video duration to capture complete rotation
            video_duration_ms = (duration + 1) * 1000

        # Start video recording with HQ camera (always use HQ for recording)
        hq_camera_id = camera_ports.get("hq", 0)
        cmd = [
            "rpicam-vid",
            "--camera", str(hq_camera_id),
            "--width", "1920",
            "--height", "1080",
            "-t", str(video_duration_ms),  # milliseconds
            "--codec", "h264",
            "-o", h264_path
        ]
        print(f"Recording 360° video with HQ camera (port {hq_camera_id})")

        # Apply current settings
        if current_wb_gains is not None:
            r_gain, b_gain = current_wb_gains
            cmd += ["--awbgains", f"{r_gain},{b_gain}"]

        if current_saturation is not None:
            sat_value = slider_to_rpicam_value(current_saturation)
            cmd += ["--saturation", str(sat_value)]

        if current_contrast is not None:
            contrast_value = slider_to_rpicam_value(current_contrast)
            cmd += ["--contrast", str(contrast_value)]

        # Apply focus lens position if set (manual focus)
        if current_focus_position is not None and current_focus_position != "0.0":
            cmd += ["--lens-position", str(current_focus_position)]
            print(f"Applying focus to video: {current_focus_position}")

        # Apply manual exposure settings if in manual mode
        if current_exposure_mode == 'manual':
            if current_shutter_speed:
                cmd += ["--shutter", str(current_shutter_speed)]
                print(f"Applying shutter to video: {current_shutter_speed}µs")
            if current_iso:
                gain = int(current_iso) / 100.0
                cmd += ["--gain", str(gain)]
                print(f"Applying ISO to video: {current_iso} (gain={gain})")

        print("Recording 360° video:", " ".join(cmd))
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            return jsonify({"error": "Recording failed", "stderr": result.stderr.decode()}), 500

        # Convert to MP4
        cmd_mp4 = [
            "ffmpeg",
            "-y",
            "-framerate", "30",
            "-i", h264_path,
            "-c", "copy",
            mp4_path
        ]
        result_mp4 = subprocess.run(cmd_mp4, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result_mp4.returncode != 0:
            return jsonify({"error": "MP4 conversion failed", "stderr": result_mp4.stderr.decode()}), 500

        # Delete h264 after conversion
        if os.path.exists(mp4_path):
            try:
                os.remove(h264_path)
            except Exception as e:
                print(f"Warning: could not delete {h264_path}: {e}")

        # If in loop mode, wait for deceleration to complete, then return to home
        if loop_mode:
            # Wait for deceleration to complete
            time.sleep(decel_time + 0.5)

            # Return to starting position
            turntable_request('/home', method='POST')
            time.sleep(return_home_time)

        # Note: Live stream will restart automatically when browser requests /video_feed
        # Give a moment for cleanup before returning
        time.sleep(0.5)

        # --- Restore HQ camera for preview ---
        restore_primary_stream()

        return jsonify({
            "message": "360° video recorded successfully",
            "mp4": os.path.basename(mp4_path),
            "duration": duration
        })

    except Exception as e:
        print(f"360° video error: {e}")
        # Stop turntable on error to prevent endless spinning
        turntable_request('/stop')
        restore_primary_stream()  # Ensure we restore even on error
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------
# Dual Camera API Endpoints
# ---------------------------------------------------------------------
@app.route('/api/cameras')
def get_cameras():
    """Return available cameras and current selection."""
    return jsonify({
        "current": current_camera,
        "available": list(camera_ports.keys()),
        "ports": camera_ports,
        "auto_switch": auto_switch_enabled
    })


@app.route('/api/camera/switch', methods=['POST'])
def switch_camera():
    """Switch to specified camera."""
    global current_camera

    try:
        data = request.get_json() or {}
        target = data.get('camera', request.form.get('camera'))

        if target not in camera_ports:
            return jsonify({"error": f"Unknown camera: {target}"}), 400

        # Kill existing stream
        subprocess.run(["pkill", "-9", "-f", "rpicam-vid"], stderr=subprocess.DEVNULL)
        time.sleep(0.5)

        current_camera = target
        print(f"Switched to camera: {current_camera} (port {camera_ports[current_camera]})")

        return jsonify({
            "message": f"Switched to {current_camera}",
            "camera": current_camera,
            "port": camera_ports[current_camera]
        })

    except Exception as e:
        print(f"Camera switch error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/camera/auto-switch', methods=['POST'])
def toggle_auto_switch():
    """Toggle auto-switch feature."""
    global auto_switch_enabled

    try:
        data = request.get_json() or {}
        enabled = data.get('enabled', request.form.get('enabled'))

        if enabled is not None:
            auto_switch_enabled = str(enabled).lower() in ('true', '1', 'yes')
        else:
            auto_switch_enabled = not auto_switch_enabled

        print(f"Auto-switch {'enabled' if auto_switch_enabled else 'disabled'}")

        return jsonify({
            "auto_switch": auto_switch_enabled
        })

    except Exception as e:
        print(f"Auto-switch toggle error: {e}")
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------
# LED Control Routes
# ---------------------------------------------------------------------

@app.route("/led/status", methods=["GET"])
def led_status():
    """Get current LED brightness."""
    result = turntable_request("/led/status", method="GET")
    return jsonify(result)

@app.route("/led/on", methods=["POST"])
def led_on():
    """Turn LED on (full brightness or specified)."""
    brightness = request.form.get("brightness")
    params = {"brightness": brightness} if brightness else None
    result = turntable_request("/led/on", params=params)
    return jsonify(result)

@app.route("/led/off", methods=["POST"])
def led_off():
    """Turn LED off."""
    result = turntable_request("/led/off")
    return jsonify(result)

@app.route("/led/brightness", methods=["POST"])
def led_brightness():
    """Set LED brightness (0-100%)."""
    value = request.form.get("value", 50)
    result = turntable_request("/led/percent", params={"value": value})
    return jsonify(result)

# Run App
# ---------------------------------------------------------------------
if __name__ == '__main__':
    # Detect available cameras at startup
    detect_cameras()

    # Change '0.0.0.0' to '<PI_IP_ADDRESS>' to bind to ethernet only
    app.run(host=FLASK_HOST, port=FLASK_PORT, threaded=True)  # From config.py