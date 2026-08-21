import cv2
import numpy as np
from typing import Optional, Tuple

import mediapipe.python.solutions.face_mesh as mp_face_mesh

class HeadPoseGazeEstimator:
    def __init__(self):
        # Initialize native MediaPipe FaceMesh
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=5,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 3D Canonical Face Model Points (mm)
        self.MODEL_POINTS_3D = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left Eye
            (225.0, 170.0, -135.0),      # Right Eye
            (-150.0, -150.0, -125.0),    # Left Mouth Corner
            (150.0, -150.0, -125.0)      # Right Mouth Corner
        ], dtype=np.float64)

        # Landmark Indices for 3D PnP alignment
        self.FACEMESH_INDICES = [1, 152, 33, 263, 61, 291]

    def estimate_head_pose(
        self, full_frame: np.ndarray, head_crop: np.ndarray
    ) -> Optional[Tuple[Tuple[int, int], np.ndarray]]:
        if head_crop is None or head_crop.size == 0:
            return None

        h, w = head_crop.shape[:2]
        rgb_crop = cv2.cvtColor(head_crop, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_crop)

        if not results.multi_face_landmarks:
            return None

        landmarks = results.multi_face_landmarks[0].landmark
        landmarks_2d = []
        
        for idx in self.FACEMESH_INDICES:
            pt = landmarks[idx]
            landmarks_2d.append([pt.x * w, pt.y * h])
            
        landmarks_2d = np.array(landmarks_2d, dtype=np.float64)

        # OpenCV solvePnP
        focal_length = float(w)
        camera_matrix = np.array([
            [focal_length, 0, w / 2.0],
            [0, focal_length, h / 2.0],
            [0, 0, 1]
        ], dtype=np.float64)
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        success, rot_vec, trans_vec = cv2.solvePnP(
            self.MODEL_POINTS_3D, landmarks_2d, camera_matrix, dist_coeffs
        )
        if not success:
            return None

        # Project 3D vector forward (1000mm)
        nose_end_point, _ = cv2.projectPoints(
            np.array([(0.0, 0.0, 1000.0)], dtype=np.float64),
            rot_vec, trans_vec, camera_matrix, dist_coeffs
        )

        gaze_x = int(nose_end_point[0][0][0])
        gaze_y = int(nose_end_point[0][0][1])

        return (gaze_x, gaze_y), landmarks_2d