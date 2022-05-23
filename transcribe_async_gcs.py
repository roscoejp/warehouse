#!/usr/bin/env python3

"""Google Cloud Speech API sample application using the REST API for batch
processing.
Example usage:
    python transcribe_async_gcs.py gs://cloud-samples-tests/speech/brooklyn.flac gs://workspace-output/brooklyn.flac
"""

import argparse
from google.cloud import speech_v1p1beta1 as speech

# Create Speech Client
def _get_impersonated_speech_client():
    target_principal = "speech-sa@rpyell-test-taoslab.iam.gserviceaccount.com"
    target_scopes = [
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/devstorage.read_write",
    ]
    return speech.SpeechClient(credentials = _get_impersonated_creds(target_principal,target_scopes))

# Get impersonation credentials
def _get_impersonated_creds(target_principal, target_scopes):
    from google.auth.impersonated_credentials import Credentials
    from google.auth import default as default_auth_creds
    default_creds, _ = default_auth_creds()
    impersonated_creds = Credentials(
        source_credentials = default_creds,
        target_principal = target_principal,
        target_scopes = target_scopes,
    )
    return impersonated_creds

# Actually do the transcription
def transcribe_to_gcs(gcs_uri_in, gcs_uri_out):
    """Asynchronously transcribes the audio file specified by `gcs_uri_in` to `gcs_uri_out`."""

    client = _get_impersonated_speech_client()

    audio = speech.RecognitionAudio(uri=gcs_uri_in)
    metadata = speech.RecognitionMetadata(
        interaction_type = speech.RecognitionMetadata.InteractionType.DISCUSSION,
        microphone_distance = (speech.RecognitionMetadata.MicrophoneDistance.NEARFIELD),
        recording_device_type = (speech.RecognitionMetadata.RecordingDeviceType.SMARTPHONE),
        recording_device_name = "Pixel 2 XL",
        industry_naics_code_of_audio = 519190,
    )
    config = speech.RecognitionConfig(
        encoding = speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz = 16000,
        language_code = "en-US",
        alternative_language_codes = ["es-US"],
        enable_automatic_punctuation = True,
        audio_channel_count = 1,
        enable_separate_recognition_per_channel = True,
        metadata = metadata,
    )
    output_config = speech.TranscriptOutputConfig(gcs_uri = gcs_uri_out)

    # long_running_recognize doesn't support output_config. See `https://github.com/googleapis/python-speech/issues/169`
    #operation = client.long_running_recognize(config=config, audio=audio, output_config=output_config)
    request = speech.LongRunningRecognizeRequest(
        audio = audio,
        config = config,
        output_config = output_config,
    )
    
    # Make the request
    operation = client.long_running_recognize(request = request)

    print("Waiting for operation to complete...")
    
    #response = operation.result(timeout = 5)

    from pprint import pprint
    pprint(operation.operation)
    return operation

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class = argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--path_in", help = "GCS path for audio file to be recognized", default = "gs://rpyell-test-taoslab-speech-to-text/workspace/input.flac")
    parser.add_argument("--path_out", help = "GCS path for output", default = "gs://rpyell-test-taoslab-speech-to-text/output/output")
    args = parser.parse_args()
    transcribe_to_gcs(args.path_in, args.path_out)
