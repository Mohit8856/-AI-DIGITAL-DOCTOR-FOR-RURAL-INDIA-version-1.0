from modules.voice_input.speech_to_text import speech_to_text

def test_voice_function():
    assert callable(speech_to_text)