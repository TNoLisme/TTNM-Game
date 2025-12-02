from uuid import UUID, uuid4

class EmotionConcept:
    def __init__(self, concept_id: UUID, emotion: str, level: int, title: str, video_path: str,
                 image_path: str, audio_path: str, description: str):
        self.concept_id = concept_id
        self.emotion = emotion
        self.level = level
        self.title = title
        self.video_path = video_path
        self.image_path = image_path
        self.audio_path = audio_path
        self.description = description

    @classmethod
    def load_concept_by_emotion_and_level(cls, emotion: str, level: int) -> 'EmotionConcept':
        """Tải khái niệm cảm xúc theo emotion và level."""
        # Placeholder: cần repository
        return cls(uuid4(), emotion, level, "Learn Emotion", "path/to/video", "path/to/image", "path/to/audio", "Description")