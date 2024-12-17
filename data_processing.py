import markdown2
import re

def split_text(text, max_tokens=4000):
    sentences = text.split('. ')
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > max_tokens:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(sentence)
        current_length += sentence_length

    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

def convert_to_markdown(data):
    markdown_lines = []
    for key, value in data.items():
        if isinstance(value, list):
            value = ", ".join(map(str, value))
        markdown_lines.append(f"**{key}**: {value}")
    return "\n\n".join(markdown_lines)

def format_with_gemini_chunks(chunks, gemini_formatter):
    formatted_results = []
    for chunk in chunks:
        try:
            formatted_result = gemini_formatter(chunk)
            formatted_results.append(formatted_result)
        except Exception as e:
            print(f"Error processing chunk: {e}")
            formatted_results.append(f"<p>Error processing this chunk: {e}</p>")
    return "\n".join(formatted_results)

import re

def validate_and_normalize_ndc(ndc_code):
    ndc_pattern = re.compile(r'^\d{4,5}-\d{3,4}-\d{1,2}$')
    
    if ndc_pattern.match(ndc_code):
        return ndc_code
    else:
        clean_ndc_code = re.sub(r'\D', '', ndc_code)
        if len(clean_ndc_code) == 11:
            return f"{clean_ndc_code[:5]}-{clean_ndc_code[5:9]}-{clean_ndc_code[9:]}"
        elif len(clean_ndc_code) == 10:
            return f"{clean_ndc_code[:5]}-{clean_ndc_code[5:8]}-{clean_ndc_code[8:]}"
        elif len(clean_ndc_code) == 9:
            return f"{clean_ndc_code[:5]}-{clean_ndc_code[5:8]}-{clean_ndc_code[8:]}"
        elif len(clean_ndc_code) == 8:
            return f"{clean_ndc_code[:4]}-{clean_ndc_code[4:7]}-{clean_ndc_code[7:]}"
        else:
            return "Invalid NDC code"