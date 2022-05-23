#!/usr/bin/env python

"""Google Cloud Speech API sample application using the REST API for batch
processing.
Example usage:
    python transcribe_async_gcs.py gs://cloud-samples-tests/speech/brooklyn.flac gs://workspace-output/brooklyn.flac
"""

import argparse

def _get_impersonated_speech_client():
    from google.cloud.speech import SpeechClient
    target_principal = "speech-sa@rpyell-test-taoslab.iam.gserviceaccount.com"
    target_scopes = [
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/devstorage.read_write",
    ]
    return SpeechClient(credentials=_get_impersonated_creds(target_principal,target_scopes))

def _get_impersonated_creds(target_principal, target_scopes):
    from google.auth.impersonated_credentials import Credentials
    from google.auth import default as default_auth_creds
    default_creds, _ = default_auth_creds()
    impersonated_creds = Credentials(
        source_credentials=default_creds,
        target_principal=target_principal,
        target_scopes=target_scopes,
    )
    return impersonated_creds

def transcribe_gcs(gcs_uri_in, gcs_uri_out):
    """Asynchronously transcribes the audio file specified by the gcs_uri_in."""
    from google.cloud import speech

    client = _get_impersonated_speech_client()

    audio = speech.RecognitionAudio(uri=gcs_uri_in)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Specifies a Cloud Storage URI for the recognition results. Must be specified in the format: `gs://bucket_name/object_name`
    output_config = speech.TranscriptOutputConfig(gcs_uri=gcs_uri_out)

    # long_running_recognize doesn't support output_config directly. See `https://github.com/googleapis/python-speech/issues/169`
    #operation = client.long_running_recognize(config=config, audio=audio, output_config=output_config)
    request = speech.LongRunningRecognizeRequest(
        audio=audio, config=config, output_config=output_config
    )
    # run the recognizer to export transcript
    operation = client.long_running_recognize(request=request)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))
        print("Confidence: {}".format(result.alternatives[0].confidence))
        from pprint import pprint
        pprint(response)


# [END speech_transcribe_async_gcs]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--path_in", help="GCS path for audio file to be recognized", default="gs://cloud-samples-tests/speech/vr.flac")
    parser.add_argument("--path_out", help="GCS path for output", default="gs://rpyell-test-taoslab-speech-to-text/output/vr.json")
    args = parser.parse_args()
    transcribe_gcs(args.path_in, args.path_out)
