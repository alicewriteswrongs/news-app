def truncate(string, length):
    if len(string) > length:
        return string[:length - 3] + "..."
    return string
