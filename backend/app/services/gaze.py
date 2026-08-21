import cv2
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

def run_gaze_estimation(source=0):
    """
    Gaze estimation using MediaPipe Face Mesh
    Estimates head pose - pitch, yaw, roll
    """
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print("Error: Could not open video source")
        return

    print("Gaze estimation started. Press Q to quit.")

    with mp_face_mesh.FaceMesh(
        max_num_faces=5,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                for face_id, face_landmarks in enumerate(results.multi_face_landmarks):

                    # Get image dimensions
                    h, w, _ = frame.shape

                    # Key landmark points for head pose estimation
                    # Nose tip, chin, left eye, right eye, left mouth, right mouth
                    face_2d = []
                    face_3d = []

                    for idx, lm in enumerate(face_landmarks.landmark):
                        if idx in [1, 33, 61, 199, 263, 291]:
                            x, y = int(lm.x * w), int(lm.y * h)
                            face_2d.append([x, y])
                            face_3d.append([x, y, lm.z])

                    face_2d = np.array(face_2d, dtype=np.float64)
                    face_3d = np.array(face_3d, dtype=np.float64)

                    # Camera matrix
                    focal_length = w
                    cam_matrix = np.array([
                        [focal_length, 0, w / 2],
                        [0, focal_length, h / 2],
                        [0, 0, 1]
                    ])

                    dist_matrix = np.zeros((4, 1), dtype=np.float64)

                    # Solve PnP to get rotation vector
                    success, rot_vec, trans_vec = cv2.solvePnP(
                        face_3d, face_2d, cam_matrix, dist_matrix
                    )

                    # Convert rotation vector to rotation matrix
                    rmat, _ = cv2.Rodrigues(rot_vec)

                    # Get angles
                    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
                    x_angle = angles[0] * 360
                    y_angle = angles[1] * 360
                    z_angle = angles[2] * 360

                    # Determine gaze direction
                    if y_angle < -10:
                        direction = "Looking LEFT"
                    elif y_angle > 10:
                        direction = "Looking RIGHT"
                    elif x_angle < -10:
                        direction = "Looking DOWN"
                    elif x_angle > 10:
                        direction = "Looking UP"
                    else:
                        direction = "Looking FORWARD (at shelf)"

                    # Print gaze info
                    print(f"Shopper #{face_id + 1} - {direction} | Pitch: {x_angle:.1f} Yaw: {y_angle:.1f}")

                    # Display on frame
                    cv2.putText(frame, direction, (10, 50 + face_id * 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Shopper #{face_id + 1}", (10, 80 + face_id * 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

                    # Trigger event when looking at shelf
                    if direction == "Looking FORWARD (at shelf)":
                        print(f"Shopper #{face_id + 1} is looking at the shelf!")

            cv2.imshow("Gaze Estimation", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Gaze estimation stopped")
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_gaze_estimation(0)