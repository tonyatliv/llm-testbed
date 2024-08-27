# llm-testbed

Python 3 interface used to extract data from PubMed publications using LLMs, part of the PubLLican project.

## Contents

[Setup](#setup)
<br />
[Configuration](#configuration)
<br />
[Running the workflow](#running-the-workflow)
<br />

## Setup

1.  Create create and activate a [virtual environment](https://docs.python.org/3/library/venv.html) if your IDE does not do so automatically

2.  Install package dependencies by running `pip install requirements.txt`

3.  Create `.env` file by running `cp .env.example .env`
    <br />_Be careful as this will overwrite your current `.env` file in case you already have one setup_

4.  Add any API keys or other environment variables to `.env` file

5.  Create a config file by running `cp config.json.example config.json`
    <br />_Be carefulas this will overwrite your current `config.json` file in case you already have one setup_

6.  Run setup script by running `python setup.py`

## Configuration

Most things are able to be configured in `config.json` if desired. The fields are pretty self-explanatory.

### Changing LLM

In the config file, there is a field called `"llm"`, which looks something like this:

```json
{
  "llm": {
    "current": {
      "type": "anthropic",
      "model": "claude-3-haiku-20240307"
    }
  },
  "rest of config.json file..."
}
```

-   The `type` parameter tells the `llms` package what model type it is and what code to run for it to work with that model. Here are the currently supported types:
    | Type | Description | Requirements |
    | --- | --- | --- |
    | `anthropic` | Anthropic's language-based models e.g. Claude | `$ANTHROPIC_API_KEY` environment variable must be set |
    | `openai` | OpenAI's language-based models e.g. ChatGPT | `$OPENAI_API_KEY` environment variable must be set |
    | `local` | Local deployment language-based models e.g. Llama | Some models may require `huggingface-cli login` |

-   The `model` parameter tells the API what specific model to use (if applicable). See documentation for more details.

**PRs adding support for more LLMs are welcome**

## Running the workflow

### **_(Pipeline for the whole workflow is coming soon. For now, the steps can be run manually.)_**

### To run the workflow manually:

1.  Download the paper. There are two options:

    -   To get the paper JSON _(preferred)_, run `python getPaperJSON.py <pmid>`
    -   To get the paper PDF, run: `python getPaperPDF.py <pmid>`

    _Note that not every publication will have a downloadable PDF, in which case getPaperJSON can be used instead_

2.  Convert the paper into plaintext

    -   If `getPaperJSON` was used, run `python getTextFromJSON.py <pmid>`

    -   If `getPaperPDF` was used, run `python getTextFromPDF.py <pmid>`
3.  Extract Summary for the paper (optional) `python getPaperSummary.py <pmid>`. This is strongly recommended if you are:
    -   Running a model whose context window is smaller than the paper's length.
    -   Usually, the model's context window is smaller than `8k`
    -   Usually, the paper's length is more than `10,000` words

4.  Query the LLM for the paper's species by running `python getPaperSpecies.py <pmid> <textSource>`

5.  Query the LLM for the paper's genes by running `python getPaperGeness.py <pmid> <textSource>`

6.  Query the LLM for the paper's GO terms by running `python getPaperGOTerms.py <pmid> <textSource>`

7.  Validate the GO terms by running `python validateGOTermDescriptions.py <pmid>`

8.  Score the similarity between model extraction and VEUPATHDB data by running `python scorePaper.py <pmid> <calculateMethod> <VDBDataFile>`
