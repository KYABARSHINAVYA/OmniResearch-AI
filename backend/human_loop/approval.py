approval_required = False


def ask_for_approval():

    global approval_required

    approval_required = True

    return {
        "status": "waiting_for_human"
    }


def approve():

    global approval_required

    approval_required = False

    return {
        "status": "approved"
    }


def is_waiting():

    return approval_required