import json
import os


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

            return json.load(f)

    except:

        return {}