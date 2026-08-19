import cv2
import time

def test_camera_stream(source=0):
    """
    Verification script to test camera/video stream ingestion.
    source=0 for webcam
    source="video.mp4" for video file
    """
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print("Error: Could not open video source")
        return

    print("Stream started successfully")
    print("Press Q to quit")

    frame_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Stream ended")
            break

        frame_count += 1
        elapsed_time = time.time() - start_time
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Log frame metadata
        print(f"Timestamp: {timestamp} | Frame: {frame_count} | Elapsed: {elapsed_time:.2f}s")

        frame = cv2.resize(frame, (640, 480))
        cv2.imshow("Camera Stream Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Stream stopped by user")
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Total frames processed: {frame_count}")


if __name__ == "__main__":
    test_camera_stream(0)