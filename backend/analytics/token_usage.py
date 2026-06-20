token_count = 0


def add_tokens(text):

    global token_count

    token_count += len(text.split())


def get_token_usage():

    return token_count