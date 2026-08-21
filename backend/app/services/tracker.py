import cv2
import time
from ultralytics import YOLO
import supervision as sv

def run_tracker(source=0):
    """
    Shopper tracking engine using YOLOv8 + ByteTrack
    source=0 for webcam
    source="video.mp4" for video file
    """
    # Load YOLOv8 model
    print("Loading YOLOv8 model...")
    model = YOLO("yolov8n.pt")  # downloads automatically first time

    # Initialize ByteTrack tracker
    tracker = sv.ByteTrack()

    # Initialize annotators for drawing boxes and labels
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    # Open video source
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print("Error: Could not open video source")
        return

    print("Tracker started. Press Q to quit.")

    # Store dwell time data
    dwell_data = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Stream ended")
            break

        # Run YOLOv8 detection — only detect persons (class 0)
        results = model(frame, classes=[0], verbose=False)[0]

        # Convert to supervision detections
        detections = sv.Detections.from_ultralytics(results)

        # Update tracker with detections
        detections = tracker.update_with_detections(detections)

        # Calculate dwell time for each tracked person
        current_time = time.time()
        for tracker_id in detections.tracker_id:
            if tracker_id not in dwell_data:
                dwell_data[tracker_id] = current_time
            dwell_time = current_time - dwell_data[tracker_id]
            print(f"Shopper #{tracker_id} - Dwell Time: {dwell_time:.1f} seconds")

        # Create labels for each detection
        labels = [
            f"Shopper #{tracker_id}"
            for tracker_id in detections.tracker_id
        ]

        # Draw bounding boxes and labels on frame
        annotated_frame = box_annotator.annotate(
            scene=frame.copy(),
            detections=detections
        )
        annotated_frame = label_annotator.annotate(
            scene=annotated_frame,
            detections=detections,
            labels=labels
        )

        # Show the frame
        cv2.imshow("Shopper Tracking", annotated_frame)

        # Press Q to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Tracker stopped by user")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Tracking session ended")
    print(f"Total shoppers tracked: {len(dwell_data)}")


if __name__ == "__main__":
    run_tracker("test_video.mp4")