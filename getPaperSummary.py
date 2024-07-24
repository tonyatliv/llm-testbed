import nltk
import os
import sys
from llms import LLMHandler
from nltk.tokenize import word_tokenize
from utils.handlers import StatusHandler, ConfigHandler


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


def getPaperSummary(pmid):
    status = StatusHandler(pmid)
    config = ConfigHandler()

    if not status.isPaperConverted():
        return ValueError("Paper has not yet been converted to plaintext")
    if status.isSummaryFetched():
        return ValueError("Summary has been fetched for this paper")

    plaintextFilePath = status.getPlaintextFilePath()
    with open(plaintextFilePath) as plaintextFile:
        plainText = plaintextFile.read()

    sectionSummarizationPrompt = config.getSectionSummarizationPromptForPaperSummary()
    totalSumarizationPrompt = config.getTotalSummarizationPromptForPaperSummary()

    words = word_tokenize(plainText)
    chunkText = " "
    page = 0
    summary = []

    while chunkText:
        page += 1
        chunkText = getChunk(words, page)
        prompt = sectionSummarizationPrompt + chunkText
        model = LLMHandler(systemPrompt=prompt)
        res = model.askWithRetry(prompt, textToComplete="Summary:")
        summary.append(res)

    totalSummary = " ".join(summary)
    prompt = totalSumarizationPrompt + totalSummary
    model = LLMHandler(systemPrompt=prompt)
    totalSummary = model.askWithRetry(prompt, textToComplete="Summary:")

    summaryFileName = f"{pmid}.txt"
    summaryFilePath = os.path.join(config.getSummaryFolderPath(), summaryFileName)
    with open(summaryFilePath, "w") as summaryFile:
        summaryFile.write(f"{totalSummary}\n")

    status.updateField("getSummary", {
        "success": True,
        "sourceFileType": "txt",
        "filename": summaryFileName
    })
    return summaryFilePath


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python getPaperSummary.py <pmid>")
        sys.exit(1)

    pmid = sys.argv[1]
    nltk.download('punkt')

    try:
        summaryPath = getPaperSummary(pmid)
        print(f"Summary for paper with PMID {pmid} is: {summaryPath}")
    except Exception as err:
        print(f"Error getting summary from paper: {err}")
