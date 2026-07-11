import os
import cv2
import numpy as np

def generate_video(filename: str, active_range: tuple, width: int = 320, height: int = 240, fps: int = 10, total_frames: int = 150):
    """Generates a dummy MP4 video with a moving red circle target during a specific frame range."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    start_frame, end_frame = active_range
    
    for frame_idx in range(total_frames):
        # Create dark background representing street view
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Draw some background lines representing lane dividers/crosswalks
        cv2.line(frame, (0, int(height/2)), (width, int(height/2)), (40, 40, 40), 2)
        cv2.putText(frame, f"{os.path.basename(filename).replace('.mp4', '')} Feed", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        cv2.putText(frame, f"Frame: {frame_idx}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (80, 80, 80), 1)
        
        # If target is active, draw it moving across
        if start_frame <= frame_idx < end_frame:
            # Linear interpolation for position
            progress = (frame_idx - start_frame) / (end_frame - start_frame)
            x = int(30 + progress * (width - 60))
            y = int(height / 2)
            
            # Draw a prominent red circle (BGR: 0, 0, 255)
            cv2.circle(frame, (x, y), 12, (0, 0, 255), -1)
            # Add a bounding box around the detected target
            cv2.rectangle(frame, (x - 18, y - 18), (x + 18, y + 18), (0, 255, 255), 1)
            cv2.putText(frame, "Target: Woman_01", (x - 40, y - 24), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
        
        out.write(frame)
        
    out.release()
    print(f"Generated video: {filename}", flush=True)

def generate_all_videos():
    video_dir = os.path.join("data", "cameras")
    
    # Camera A active from frame 0 to 50
    generate_video(os.path.join(video_dir, "Camera_A.mp4"), (0, 50))
    # Camera B active from frame 50 to 100
    generate_video(os.path.join(video_dir, "Camera_B.mp4"), (50, 100))
    # Camera C active from frame 100 to 150
    generate_video(os.path.join(video_dir, "Camera_C.mp4"), (100, 150))

if __name__ == "__main__":
    generate_all_videos()
