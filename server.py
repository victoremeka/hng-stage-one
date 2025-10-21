from datetime import datetime, timezone
import re
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
import hashlib
import uuid

app = FastAPI()

strings = {}

@app.get("/")
def index():
    return JSONResponse({"message": "welcome to string analyzer"})

@app.post("/strings", status_code=201)
def analyze_string(payload: dict):
    input_string = payload.get("value", None)

    if type(input_string) != str:
        return JSONResponse(
            content={"message": "Invalid data type for 'value' (must be string)"},
            status_code=422
        )

    if input_string in strings:
        return JSONResponse(
            content={
            "message": "String already exists in the system",
            },
            status_code=409,     
        )
    if input_string:
        
        sha256_hash = hashlib.sha256(input_string.encode()).hexdigest()
        is_palindrome = input_string == input_string[::-1]
        unique_characters  = len(set(input_string))
        word_count = len(input_string.split())
        string_length = len(input_string)
        created_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        character_frequency_map = {}
        for k in input_string:
            character_frequency_map[k] = character_frequency_map.get(k, 0) + 1

        content = {
            "id": uuid.uuid4().int,
            "value": input_string,
            "properties": {
                "length": string_length,
                "is_palindrome": is_palindrome,
                "unique_characters": unique_characters,
                "word_count": word_count,
                "sha256_hash": sha256_hash,
                "character_frequency_map": character_frequency_map,
            },
            "created_at": created_at
        }

        strings[input_string]=content
        headers = {
            "Content-Type": "application/json"
        }
        
        return JSONResponse(
            content=content,
            headers=headers,
            status_code=201
        )
    return JSONResponse(
        content={"message":"Invalid request body or missing 'value' field"},
        status_code=400
    )

@app.get("/strings")
def get_all_strings(
    is_palindrome: bool | None = None, 
    min_length: int | None = None, 
    max_length: int | None = None, 
    word_count: int | None = None, 
    contains_character: str | None = None):
    if None in (is_palindrome, min_length, max_length, word_count, contains_character):
        return JSONResponse(
            content={
                "message": "Invalid query parameter values or types",
            },
            status_code=400,
        )

    filtered_strings = []
    for x in strings:
        string_properties = strings[x]["properties"]
        s_ispalindrome = string_properties["is_palindrome"] == is_palindrome
        s_isminlength = string_properties["length"] >= min_length
        s_ismaxlength = string_properties["length"] <= max_length
        s_wordcount = string_properties["word_count"] == word_count
        s_containschar = contains_character in string_properties["character_frequency_map"]

        if s_containschar and s_wordcount and s_ismaxlength and s_isminlength and s_ispalindrome:
            filtered_strings.append(x)
    
    content = {
        "data": filtered_strings,
        "count": len(filtered_strings),
        "filters_applied": {
            "is_palindrome": is_palindrome,
            "min_length": min_length,
            "max_length": max_length,
            "word_count": word_count,
            "contains_character": contains_character
        }
    }

    return JSONResponse(
        content=content
    )



@app.get("/strings/filter-by-natural-language")
def get_all_strings_by_nlp(query: str):
    try:
        parsed_filters = {}
        query_lower = query.lower()

        if "palindrom" in query_lower:
            print("aaa")
            parsed_filters["is_palindrome"] = True
        
        if "single word" in query_lower:
            parsed_filters["word_count"] = 1
        elif match := re.search(r'(\d+)\s+word', query_lower):
            parsed_filters["word_count"] = int(match.group(1))
        
        if match := re.search(r'longer than (\d+)', query_lower):
            parsed_filters["min_length"] = int(match.group(1)) + 1
        if match := re.search(r'shorter than (\d+)', query_lower):
            parsed_filters["max_length"] = int(match.group(1)) - 1
        
        if match := re.search(r'contain(?:ing|s)?\s+(?:the\s+letter\s+)?([a-z])', query_lower):
            parsed_filters["contains_character"] = match.group(1)
        elif "first vowel" in query_lower:
            parsed_filters["contains_character"] = "a"
        
        if not parsed_filters:
            return JSONResponse(
                content={"message": "Unable to parse natural language query"},
                status_code=400
            )
        
        filtered = []
        for string_data in strings.values():
            props = string_data["properties"]
            value = string_data["value"]
            
            if "is_palindrome" in parsed_filters:
                if props["is_palindrome"] != parsed_filters["is_palindrome"]:
                    continue
            
            if "word_count" in parsed_filters:
                if props["word_count"] != parsed_filters["word_count"]:
                    continue
            
            if "min_length" in parsed_filters:
                if props["length"] < parsed_filters["min_length"]:
                    continue
            
            if "max_length" in parsed_filters:
                if props["length"] > parsed_filters["max_length"]:
                    continue
            
            if "contains_character" in parsed_filters:
                if parsed_filters["contains_character"] not in value.lower():
                    continue
            
            filtered.append(string_data)
        
        return JSONResponse({
            "data": filtered,
            "count": len(filtered),
            "interpreted_query": {
                "original": query,
                "parsed_filters": parsed_filters
            }
        })
    
    except Exception as e:
        return JSONResponse(
            content={"message": "Unable to parse natural language query"},
            status_code=400
        )    


@app.get("/strings/{string_value}")
def get_string(string_value):
    if string_value not in strings:
        return JSONResponse(
            content={"message": "String does not exist in the system"},
            status_code=404
        )
    
    return JSONResponse(
        content=strings[string_value]
    )
    

@app.delete("/strings/{string_value}")
def delete_string(string_value):
    if string_value not in strings:
        return JSONResponse(
            content={"message": "String does not exist in the system"},
            status_code=404
        )
    
    strings.pop(string_value)
    
    return Response(
        status_code=204,
        headers={
            "Content-Type":"application/json"
        }
    )