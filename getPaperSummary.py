def getChunk(words, page):
    overlap = 200
    chunkSize = 1200
    start = page * chunkSize - overlap
    if start < 0:
        start = 0
    if start >= len(words):
        return ""
    while (start > 1) and not words[start - 1].endswith("."):
        start = start - 1

    end = page * chunkSize + overlap
    if end >= len(words):
        end = len(words) - 1

    while end < len(words) and not words[end].endswith("."):
        end = end + 1

    chunk_text = " ".join(words[start:end + 1])
    return chunk_text


def getWords(text):
    words = text.split(" ")
    return words


def getPaperSummary(plainText):
    words = getWords(plainText)
    chunkText = " "
    page = 0
    summary = []
    genes = set()
    getChunk(words, page)