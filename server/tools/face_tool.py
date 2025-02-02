import face_recognition
import glob
import numpy as np
from server.type.singletone import Singleton
from .face_list import FaceList


class _FaceTool():
    def __init__(self, init):
        self.faceList = FaceList(3,"server/tools/faceData")
        self.contextFaceList = self.faceList.getFaceDataList()
        encodings = list(map(lambda x: x[1]["faceEncoding"] if x[1].get("faceEncoding") is not None else np.zeros(128, dtype=np.float64), self.contextFaceList))
    
    @staticmethod
    def feature(frame):
        rgb_frame = frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_frame, number_of_times_to_upsample=0)
        
        if face_locations == []:
            return None
                
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        return face_encodings

    def sync(self):
        print("SYNC")
        self.faceList.syncServer()
        self.contextFaceList = self.faceList.getFaceDataList()

    def match(self, landmark):
        data = {"mno": 0, "name": "Unknown"}

        if landmark is None:
            return data, False
        
        encodings = list(map(lambda x: x[1]["faceEncoding"] if x[1].get("faceEncoding") is not None else np.zeros(128, dtype=np.float64), self.contextFaceList))
        face_distances = face_recognition.face_distance(encodings, self.__convertListLandmark(landmark))
        best_match_index = np.argmin(face_distances)
        if face_distances[best_match_index] <= 0.35:
            print(face_distances[best_match_index])
            data = self.contextFaceList[best_match_index][1]
        
        return data, float(face_distances[best_match_index])

    def __convertListLandmark(self, listLandmark):
        return np.array(listLandmark)


class FaceTool(_FaceTool, Singleton):
    pass
