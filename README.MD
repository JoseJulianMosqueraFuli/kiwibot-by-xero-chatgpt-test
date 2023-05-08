# Kiwibot-by-Xero-OpenAi-ChatGPT

This is a sample API built using Python and FastAPI, consuming OpenAI. It feature endpoint to chat with ChatGPT.

## Disclaimer

**Important:** Please note that the information provided by the Kiwibot-by-Xero-OpenAi-ChatGPT project is subject to certain limitations. Due to the lack of access to the requirements provided by Kiwibot and the information of the AI model itself.

## Overview:

In this document you can find a detailed explanation of the project setup, technologies and available features.
This is the API built up to the deadline of the case study, in branch master.

## Index

1. [ Project sample ](#sample)
2. [ Getting started ](#getting-started)
3. [ Available endpoints ](#available-endpoints)

## Sample

In building for the moment

## Getting started

To run this API on your local machine, follow these steps:

1. Clone the repository:

```bash
git clone git@github.com:JoseJulianMosqueraFuli/kiwibot-by-xero-chatgpt-test.git
```

2. Navigate into the cloned directory:

```bash
cd kiwibot-by-xero-chatgpt-test
```

3. Create a `.env` file like `.env.example` :

```python
OPEN_API_KEY =
```

4. Build and run the Docker container:

```bash
docker-compose up --build
```

5. The API should now be available at http://localhost:8000.\*

## Available endpoints

### OpenAI

#### POST

```jsx
http://127.0.0.1:8000/openai
```

```jsx
{
  "content": "how you can describe kiwibot company?"
}
```
