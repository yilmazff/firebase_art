# Installation
Install the required packages with `pip install -r requirements.txt`.

Image search requires a Bing Image Search API v7 key.

1. Please obtain your key by following the instructions in the [Microsoft Build Documentation](https://docs.microsoft.com/en-us/rest/api/cognitiveservices-bingsearch/bing-images-api-v7-reference).
2. Once you obtain your API key, please store it in `./metadata/bing_api_key.json` as a dictionary with item `"key" : <YOUR_BING_API_KEY>`.

# Usage
The [firebase_examples notebook](./firebase_examples.ipynb) contains example documents and code to execute the FIREBASE pipeline and visualize the results.


# License
**Important**: Images acquired from the web through the FIREBASE platform are subject to their own license and copyrights may apply. 

This repository is published under [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
