class MemoryScorer:
  """Memory Scoring Engine for LoopChamber"""

  def __init__(self):
      # Emotional lexicons for detecting emotions
      self.emotional_lexicons = {
          "positive": [
              "happy", "joy", "glad", "delight", "pleased", "cheerful", "content",
              "satisfied", "excited", "thrilled", "optimistic", "enthusiastic",
              "hopeful", "confident", "proud", "love", "adore", "enjoy", "like"
          ],
          "negative": [
              "sad", "unhappy", "depressed", "gloomy", "miserable", "disappointed",
              "frustrated", "annoyed", "angry", "furious", "outraged", "irritated",
              "upset", "worried", "anxious", "afraid", "fearful", "scared"
          ],
          "neutral": [
              "think", "consider", "believe", "understand", "know", "recognize",
              "observe", "notice", "perceive", "feel", "sense", "experience"
          ],
          "complex": [
              "bittersweet", "ambivalent", "conflicted", "torn", "mixed feelings",
              "nostalgic", "melancholy", "sentimental", "wistful", "longing"
          ]
      }

      # Contradiction signals
      self.contradiction_signals = [
          "but", "however", "nevertheless", "conversely", "on the other hand",
          "in contrast", "contrary", "opposite", "unlike", "instead", 
          "while", "whereas", "yet", "although", "despite", "in spite"
      ]

  def score_memory(self, content, memory_type, existing_memories=None):
      """Score a memory based on musical attributes"""
      # Text preprocessing
      text = content.lower()
      word_count = len(text.split())

      # ====== PITCH (relevance/salience) ======
      # Length factor (longer text often has more substance)
      length_factor = min(1.0, max(0.1, word_count / 100))

      # Memory type factor
      type_weights = {
          "insight": 0.8,      # Insights are typically high relevance
          "question": 0.7,     # Questions are exploratory
          "observation": 0.6,  # Observations are contextual
          "event": 0.5,        # Events are factual
          "reflection": 0.7    # Reflections are introspective
      }
      type_factor = type_weights.get(memory_type.lower(), 0.5)

      # Calculate pitch from factors
      pitch = (length_factor * 0.4) + (type_factor * 0.6)

      # ====== DISSONANCE (contradiction/conflict) ======
      # Internal contradiction score
      contradiction_score = 0
      for signal in self.contradiction_signals:
          if signal in text:
              contradiction_score += 0.15
      contradiction_score = min(0.8, contradiction_score)

      # Calculate dissonance score (simplified version)
      dissonance = max(0.1, min(0.9, contradiction_score))

      # ====== TEMPO (recall frequency) ======
      # Question marks increase tempo (they prompt thinking)
      question_factor = min(0.8, text.count('?') * 0.2)

      # Memory type factor for tempo
      tempo_type_weights = {
          "insight": 0.7,     # Insights are revisited often
          "question": 0.8,    # Questions prompt frequent returns
          "observation": 0.5,  # Observations less often
          "event": 0.4,       # Events are recalled less frequently
          "reflection": 0.6    # Reflections are revisited
      }
      tempo_type_factor = tempo_type_weights.get(memory_type.lower(), 0.5)

      # Calculate tempo
      tempo = (question_factor * 0.4) + (tempo_type_factor * 0.6)

      # ====== EMOTION (emotional charge) ======
      # Determine the dominant emotion based on emotional keywords
      emotion_counts = {category: 0 for category in self.emotional_lexicons.keys()}

      for category, words in self.emotional_lexicons.items():
          for word in words:
              if word in text:
                  emotion_counts[category] += 1

      # Find dominant emotion
      dominant_emotion = "neutral"
      max_count = 0

      for emotion, count in emotion_counts.items():
          if count > max_count:
              max_count = count
              dominant_emotion = emotion

      # Compile the final scores
      scores = {
          "pitch": round(pitch, 2),
          "dissonance": round(dissonance, 2),
          "tempo": round(tempo, 2),
          "emotion": dominant_emotion
      }

      return scores