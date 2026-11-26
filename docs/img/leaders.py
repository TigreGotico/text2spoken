"""The leader languages, which come first on docs/coverage.md, in their fixed order."""
LEADER_TAGS = ("pt-PT", "pt-BR", "es-CO", "fr-FR", "it-IT", "de-DE", "nl-NL", "da-DK", "kab", "hi-IN", "bn-IN", "mwr")
LEADER_FILES = ("pt", "es", "fr", "it", "de", "nl")
NO_FILE_TAGS = ("da-DK", "kab", "hi-IN", "bn-IN", "mwr")


def leaders_first(codes, key):
    """Sort codes by key, then move the leader files to the end, so that a bottom-up plot shows them on top."""
    rest = sorted((code for code in codes if code not in LEADER_FILES), key=key)
    return rest + [code for code in reversed(LEADER_FILES) if code in codes]
