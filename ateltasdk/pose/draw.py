import cv2 
import math 
import numpy as np
import mediapipe as mp 
import matplotlib.pyplot as plt 

from fastdtw import fastdtw
from scipy.spatial import procrustes
from scipy.spatial.distance import euclidean

from typing import List, Tuple, Optional, NamedTuple, Dict, Union 

# mediapipe libraries

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

class PoseDraw:
    """
    Mediapipe is limited when it comes to drawing pose landmarks. Pose landmarks generated by mediapipe 
    is wrapped by a specific class type. But suppose our landmarks is a json object or a numpy array. What we
    gonna do in that case. The class Draw helps to deal with that.
    """
    def __init__(self) -> None:
        ... 
    
    def draw_mediapipe_pose(self, image : np.ndarray, results : NamedTuple) -> np.ndarray:
        """
        Draws default mediapipe pose
        """
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2),
        )
        return image
    
    def convert_pose_landmark_to_list(self, pose_results : NamedTuple) -> List[List[float]]:
        """Converts medapipe results (results.pose_landmarks.landmark) to a list

        Args:
            pose_results (results.pose_landmarks.landmark): Mediapipe results

        Returns:
            _List[float] : List of floats of that results containing the (x, y, z) coordinates
        """
        landmarks = []
        for landmark in pose_results.pose_landmarks.landmark:
            landmarks.append((landmark.x, landmark.y))
        return landmarks
    

    def draw_custom_landmark(
        self, 
        image: np.ndarray,
        landmarks: List[Tuple[int, int]],
        connection: List[Tuple[int, int]] = mp_pose.POSE_CONNECTIONS,
        indices_to_avoid_nodes: List[int] = None,
        indices_to_avoid_edges: List[int] = None,
        dot_color: Tuple[int, int, int] = (0, 255, 0),
        line_color: Tuple[int, int, int] = (0, 0, 255),
        diameter: int = 6,
        line_width: int = 3,
    ) -> np.ndarray:
        """Drawing custom landmarks

        image : numpy.ndarray,
        landmarks : mediapipe_landmarks.landmark,
        indices_to_avoid_nodes : the indices to avoid during drawing for the nodes,
        indices_to_avoid_edges : the indices to avoid during drawing for the edges,
        dot_color : the color of the nodes,
        line_color : the color of the edges,
        diameter : the diameter of the circle of the nodes,
        line_width : the width of the circle

        Returns:
            np.ndarray: The annotated image
        """

        # TODO : draw a trivial edge as a hand to palm joint
        # TODO : Have to make compatible with multi landmarks, though it could be done explicitely

        height, width, _ = image.shape
        connection = list(connection)
        keypoints = []

        if landmarks is not None:
            for idx, landmark in enumerate(landmarks):
                x, y = landmark

                x_px = int(min(math.floor(x * width), width - 1))
                y_px = int(min(math.floor(y * height), height - 1))
                keypoints.append((x_px, y_px))

                if indices_to_avoid_nodes is not None and idx in indices_to_avoid_nodes:
                    continue

                else:
                    cv2.circle(image, (int(x_px), int(y_px)), diameter, dot_color, -1)

            for inx, conn in enumerate(connection):
                from_ = conn[0]
                to_ = conn[1]
                if indices_to_avoid_edges is not None and from_ in indices_to_avoid_edges:
                    continue
                else:
                    if keypoints[from_] and keypoints[to_]:
                        cv2.line(image, keypoints[from_], keypoints[to_], line_color, line_width)
                    else:
                        continue
        return image