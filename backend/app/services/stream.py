import cv2
import time


def stream_video(source=0):
    """
    Stream video from a webcam or video file.
    source=0 means webcam
    source="path/to/video.mp4" means a video file
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
            print("Stream ended or cannot read frame")
            break

        frame_count += 1
        elapsed_time = time.time() - start_time
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        print(f"Timestamp: {timestamp} | Frame: {frame_count} | Elapsed: {elapsed_time:.2f}s")

        frame = cv2.resize(frame, (640, 480))
        cv2.imshow("Consumer Attention Mapping - Stream", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Stream stopped by user")
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Total frames processed: {frame_count}")


if __name__ == "__main__":
    stream_video(0)