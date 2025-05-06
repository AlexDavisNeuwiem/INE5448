import cv2

class FingerprintRecognizer:
    def __init__(self):
        self.database = {}
        self.similarity_threshold = 0.7

    def add_person(self, name, path):
        img = self._load_fingerprint(path)
        if img is not None:
            self.database[name] = img
            return True
        return False
    
    def recognize(self, path):
        img = self._load_fingerprint(path)
        if img is None:
            return None, 0
        best_match = None
        best_similarity = 0.0
        for name, stored_img in self.database.items():
            sim = self._calculate_similarity(stored_img, img)
            if sim > best_similarity:
                best_match = name
                best_similarity = sim
        if best_similarity >= self.similarity_threshold:
            return best_match, best_similarity
        return None, best_similarity

    def verify(self, path, name):
        img = self._load_fingerprint(path)
        if img is None:
            return False, 0
        similarity = self._calculate_similarity(self.database[name], img)
        belongs = False
        if similarity >= self.similarity_threshold:
            belongs = True
        return belongs, similarity

    def _load_fingerprint(self, path):
        """Load and preprocess the fingerprint image"""
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None
        return cv2.resize(img, (200, 200))

    def _calculate_similarity(self, img1, img2):
        """Compare two fingerprint images and return similarity"""
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)

        if des1 is None or des2 is None:
            return 0.0

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)

        if not matches:
            return 0.0

        good_matches = [m for m in matches if m.distance < 60]
        similarity = len(good_matches) / max(len(des1), len(des2))
        return similarity