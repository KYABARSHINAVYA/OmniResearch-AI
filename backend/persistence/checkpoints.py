import json
import os


def _clean_loaded_checkpoint(value):
    if isinstance(value, dict):
        return {
            key: _clean_loaded_checkpoint(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [_clean_loaded_checkpoint(item) for item in value]

    if isinstance(value, str):
        text = value.lower()
        if (
            "insufficient_quota" in text
            or "exceeded your current quota" in text
            or "error code: 429" in text
        ):
            return (
                "Previous run failed because the selected language model "
                "provider was out of quota."
            )

    return value


def save_checkpoint(state):

    print("SAVING CHECKPOINT")
    print(state)

    filepath = os.path.join(
        os.getcwd(),
        "checkpoint.json"
    )

    with open(
            filepath,
            "w"
    ) as f:

        json.dump(
            state,
            f,
            indent=4,
            default=str
        )


def load_checkpoint():

    filepath = os.path.join(
        os.getcwd(),
        "checkpoint.json"
    )

    try:

        with open(
                filepath,
                "r"
        ) as f:

            return _clean_loaded_checkpoint(json.load(f))

    except:

        return {}
