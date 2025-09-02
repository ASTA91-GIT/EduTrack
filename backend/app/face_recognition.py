import face_recognition
import numpy as np
from sqlalchemy.orm import Session
from . import models

class FaceRecognitionService:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_ids = []
    
    def load_known_faces(self, db: Session):
        """Load all known face encodings from database"""
        users = db.query(models.User).filter(models.User.face_encoding.isnot(None)).all()
        self.known_face_encodings = []
        self.known_face_ids = []
        
        for user in users:
            if user.face_encoding:
                self.known_face_encodings.append(np.array(user.face_encoding))
                self.known_face_ids.append(user.id)
    
    def recognize_face(self, image_path, db: Session):
        """Recognize face from image"""
        # Load the uploaded image
        image = face_recognition.load_image_file(image_path)
        
        # Find all the faces and face encodings in the current frame
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        recognized_faces = []
        
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            
            # Find the best match
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                user_id = self.known_face_ids[best_match_index]
                confidence = 1 - face_distances[best_match_index]
                
                recognized_faces.append({
                    "user_id": user_id,
                    "confidence": confidence
                })
        
        return recognized_faces
    
    def create_face_encoding(self, image_path):
        """Create face encoding from image"""
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        
        if len(face_encodings) > 0:
            return face_encodings[0].tolist()
        return None

# Global instance
face_service = FaceRecognitionService()