from google.cloud import texttospeech_v1


async def sample_synthesize_speech(text, name, speed):
    # Create a client
    client = texttospeech_v1.TextToSpeechAsyncClient()

    # Initialize request argument(s)
    input = texttospeech_v1.SynthesisInput()
    input.text = text

    voice = texttospeech_v1.VoiceSelectionParams()
    voice.language_code = "en-US"
    voice.ssml_gender = texttospeech_v1.SsmlVoiceGender.NEUTRAL

    audio_config = texttospeech_v1.AudioConfig()
    audio_config.audio_encoding = "ALAW"
    audio_config.speaking_rate = speed

    request = texttospeech_v1.SynthesizeSpeechRequest(
        input=input,
        voice=voice,
        audio_config=audio_config,
    )
    response = await client.synthesize_speech(request=request)
    with open(f"mp3/{name}", "wb") as out:
        out.write(response.audio_content)
