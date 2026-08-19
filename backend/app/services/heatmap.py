import numpy as np
import cv2
import os
from ultralytics import YOLO

def generate_heatmap(width=640, height=480, output_path="heatmap.png", show_window=False):
    """
    Generate a store attention heatmap by processing test_video.mp4
    using YOLOv8 person detection.
    Red = high traffic/attention
    Blue = low traffic
    """

    # Path to video and model
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    video_path = os.path.join(base_dir, "test_video.mp4")
    model_path = os.path.join(base_dir, "yolov8n.pt")

    heatmap_data = np.zeros((height, width), dtype=np.float32)

    # Try to process real video
    if os.path.exists(video_path) and os.path.exists(model_path):
        print(f"Processing video: {video_path}")
        model = YOLO(model_path)
        cap = cv2.VideoCapture(video_path)

        frame_count = 0
        max_frames = 300  # Process up to 300 frames

        while cap.isOpened() and frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            frame_resized = cv2.resize(frame, (width, height))
            results = model(frame_resized, classes=[0], verbose=False)  # class 0 = person

            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    confidence = float(box.conf[0])

                    # Add heat at person's center position
                    for i in range(max(0, cy - 40), min(height, cy + 40)):
                        for j in range(max(0, cx - 40), min(width, cx + 40)):
                            dist = np.sqrt((i - cy) ** 2 + (j - cx) ** 2)
                            if dist < 40:
                                heatmap_data[i, j] += confidence * np.exp(-dist ** 2 / (2 * 15 ** 2))

            frame_count += 1
            if frame_count % 30 == 0:
                print(f"Processed {frame_count} frames...")

        cap.release()
        print(f"Video processing complete. Total frames: {frame_count}")

    else:
        # Fallback to simulated data if video not found
        print("Video or model not found, using simulated data")
        shopper_positions = [
            (100, 100, 0.9), (120, 110, 0.8), (110, 90, 0.85),
            (130, 120, 0.7), (90, 100, 0.75), (105, 115, 0.8),
            (250, 200, 0.5), (270, 210, 0.45), (260, 190, 0.55),
            (240, 215, 0.4),
            (400, 300, 0.2), (420, 310, 0.15), (410, 290, 0.25),
            (500, 150, 1.0), (520, 160, 0.95), (510, 140, 0.9),
            (490, 170, 0.85), (530, 155, 0.88), (505, 145, 0.92),
            (580, 400, 0.1), (590, 410, 0.08),
        ]
        for (x, y, intensity) in shopper_positions:
            for i in range(max(0, y - 50), min(height, y + 50)):
                for j in range(max(0, x - 50), min(width, x + 50)):
                    dist = np.sqrt((i - y) ** 2 + (j - x) ** 2)
                    if dist < 50:
                        heatmap_data[i, j] += intensity * np.exp(-dist ** 2 / (2 * 20 ** 2))

    # Normalize and colorize
    heatmap_data = cv2.normalize(heatmap_data, None, 0, 255, cv2.NORM_MINMAX)
    heatmap_data = heatmap_data.astype(np.uint8)
    heatmap_colored = cv2.applyColorMap(heatmap_data, cv2.COLORMAP_JET)

    # Add labels
    cv2.putText(heatmap_colored, "Aisle 1 - Snacks", (70, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(heatmap_colored, "Aisle 2 - Beverages", (210, 180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(heatmap_colored, "Aisle 3 - Dairy", (360, 280),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(heatmap_colored, "Aisle 4 - Bakery (HOT)", (440, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(heatmap_colored, "Aisle 5 - Frozen", (530, 380),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(heatmap_colored, "STORE ATTENTION HEATMAP", (180, 460),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imwrite(output_path, heatmap_colored)
    print(f"Heatmap saved to {output_path}")

    if show_window:
        cv2.imshow("Store Attention Heatmap", heatmap_colored)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return output_path


if __name__ == "__main__":
    generate_heatmap(output_path="heatmap.png", show_window=True)