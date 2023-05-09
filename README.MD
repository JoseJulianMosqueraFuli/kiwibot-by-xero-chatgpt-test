# Kiwibot-by-Xero-OpenAi-ChatGPT

This is a sample API built using Python and FastAPI, consuming OpenAI. It features an endpoint to chat with ChatGPT to support report problem for kiwi.

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
OPEN_API_KEY = <your_openai_api_key>
```

4. Build and run the Docker container:

```bash
docker-compose up --build
```

5. The API should now be available at http://localhost:8000.\*

## Available endpoints

### Problem Report Endpoint

#### POST /problem-report

```jsx
http://localhost:8000/problem-report
```

Input

```jsx
{
  "content": "I'm experiencing a hardware issue with my Kiwibot at location NY. The issue is related to the wheels not moving properly. I noticed this problem when the bot was attempting to navigate uneven surfaces. The wheels seem to get stuck frequently. Please generate a formatted ticket with all the necessary details for the support team to address this issue.",
  "heartbeat": {
    "bot_id": "abc123",
    "timestamp": "2023-05-08T10:00:00Z",
    "location": {
      "lat": 40.731,
      "lon": -73.997
    },
    "status": "available",
    "battery_level": 80.08,
    "software_version": "v1.0",
    "hardware_version": "v2.0"
  }
}
```

Response Ticket

```jsx
{
    "ticket_id": "e79cba84-511c-45a0-a6ea-ec3997cac854",
    "problem_location": "New York University, Bond Street, Manhattan Community Board 2, Manhattan, New York County, City of New York, New York, 10012, United States",
    "problem_type": "hardware",
    "summary": "Issue Report Ticket:\n\nLocation: NY\n\nType of Issue: Hardware\n\nDescription: The wheels of the kiwibot are not moving properly. The bot seems to get stuck frequently while navigating uneven surfaces. \n\nSteps Taken: I have tried restarting the bot, but the issue persists. \n\nAdditional Information: The kiwibot was working fine before this issue occurred. No recent updates have been made to the software. \n\nPlease address this issue as soon as possible.",
    "bot_id": "abc123",
    "status": "open"
}
```
