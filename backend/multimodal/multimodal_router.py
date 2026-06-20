from multimodal.image_agent import process_image
from multimodal.audio_agent import audio_to_text
from multimodal.ocr_agent import extract_text


def route_input(
        file_type,
        file_path
):

    if file_type == "image":

        return process_image(file_path)

    elif file_type == "ocr":

        return extract_text(file_path)

    elif file_type == "audio":

        return audio_to_text(file_path)

    else:

        return "Unsupported file type"