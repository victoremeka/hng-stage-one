# Stage 1: String Analyzer Service

A RESTful API service that analyzes strings and stores their computed properties.

## Features

For each analyzed string, the service computes and stores:
- **length**: Number of characters in the string
- **is_palindrome**: Boolean indicating if the string reads the same forwards and backwards (case-insensitive)
- **unique_characters**: Count of distinct characters in the string
- **word_count**: Number of words separated by whitespace
- **sha256_hash**: SHA-256 hash of the string for unique identification
- **character_frequency_map**: Object/dictionary mapping each character to its occurrence count

## API Endpoints

### 1. Create/Analyze String
**POST** `/strings`

Analyzes and stores a new string.

**Request Body:**
```json
{
  "value": "string to analyze"
}
```

**Success Response (201 Created):**
```json
{
  "id": "sha256_hash_value",
  "value": "string to analyze",
  "properties": {
    "length": 17,
    "is_palindrome": false,
    "unique_characters": 12,
    "word_count": 3,
    "sha256_hash": "abc123...",
    "character_frequency_map": {
      "s": 2,
      "t": 3,
      "r": 2
    }
  },
  "created_at": "2025-08-27T10:00:00Z"
}
```

**Error Responses:**
- `409 Conflict`: String already exists in the system
- `400 Bad Request`: Invalid request body or missing "value" field
- `422 Unprocessable Entity`: Invalid data type for "value" (must be string)

### 2. Get Specific String
**GET** `/strings/{string_value}`

Retrieves a previously analyzed string.

**Success Response (200 OK):**
```json
{
  "id": "sha256_hash_value",
  "value": "requested string",
  "properties": { /* ... */ },
  "created_at": "2025-08-27T10:00:00Z"
}
```

**Error Response:**
- `404 Not Found`: String does not exist in the system

### 3. Get All Strings with Filtering
**GET** `/strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a`

Retrieves all strings that match the provided filters.

**Query Parameters (all optional):**
- `is_palindrome`: boolean (true/false)
- `min_length`: integer (minimum string length)
- `max_length`: integer (maximum string length)
- `word_count`: integer (exact word count)
- `contains_character`: string (single character to search for)

**Success Response (200 OK):**
```json
{
  "data": [
    {
      "id": "hash1",
      "value": "string1",
      "properties": { /* ... */ },
      "created_at": "2025-08-27T10:00:00Z"
    }
  ],
  "count": 15,
  "filters_applied": {
    "is_palindrome": true,
    "min_length": 5,
    "max_length": 20,
    "word_count": 2,
    "contains_character": "a"
  }
}
```

**Error Response:**
- `400 Bad Request`: Invalid query parameter values or types

### 4. Natural Language Filtering
**GET** `/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings`

Filters strings using natural language queries.

**Example Queries:**
- "all single word palindromic strings" → `word_count=1, is_palindrome=true`
- "strings longer than 10 characters" → `min_length=11`
- "palindromic strings that contain the first vowel" → `is_palindrome=true, contains_character=a`
- "strings containing the letter z" → `contains_character=z`

**Success Response (200 OK):**
```json
{
  "data": [ /* array of matching strings */ ],
  "count": 3,
  "interpreted_query": {
    "original": "all single word palindromic strings",
    "parsed_filters": {
      "word_count": 1,
      "is_palindrome": true
    }
  }
}
```

**Error Responses:**
- `400 Bad Request`: Unable to parse natural language query
- `422 Unprocessable Entity`: Query parsed but resulted in conflicting filters

### 5. Delete String
**DELETE** `/strings/{string_value}`

Deletes a previously analyzed string.

**Success Response:** `204 No Content` (Empty response body)

**Error Response:**
- `404 Not Found`: String does not exist in the system

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Dependencies
Install the required packages:
```bash
pip install fastapi uvicorn
```

Or using the `pyproject.toml`:
```bash
pip install -e .
```

### Running Locally

1. Clone the repository:
```bash
git clone <repository-url>
cd hng/stage1
```

2. Install dependencies:
```bash
pip install fastapi uvicorn
```

3. Run the server:
```bash
uvicorn server:app --reload
```

The API will be available at `http://localhost:8000`

4. View API documentation:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Environment Variables
No environment variables are required for basic operation. The service uses in-memory storage.

## Tech Stack
- **Framework**: FastAPI
- **Language**: Python 3.10+
- **Server**: Uvicorn (ASGI server)

## Testing

You can test the endpoints using:
- **cURL**
- **Postman**
- **HTTPie**
- **FastAPI's built-in Swagger UI** at `/docs`

### Example cURL Commands:

**Analyze a string:**
```bash
curl -X POST http://localhost:8000/strings \
  -H "Content-Type: application/json" \
  -d '{"value": "hello world"}'
```

**Get a string:**
```bash
curl http://localhost:8000/strings/hello%20world
```

**Filter strings:**
```bash
curl "http://localhost:8000/strings?is_palindrome=true&word_count=1"
```

**Natural language query:**
```bash
curl "http://localhost:8000/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings"
```

**Delete a string:**
```bash
curl -X DELETE http://localhost:8000/strings/hello%20world
```

## Notes
- The service uses in-memory storage, so data is lost when the server restarts
- String values are used as unique identifiers (case-sensitive)
- Palindrome checking is case-sensitive
- Character frequency map includes all characters (spaces, punctuation, etc.)