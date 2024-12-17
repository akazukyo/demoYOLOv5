import requests
import urllib.parse
from data_processing import convert_to_markdown, split_text, format_with_gemini_chunks
from gemini_interaction import format_with_gemini

def get_set_id_from_dailymed_json(package_ndc_code):
    url = f"https://dailymed.nlm.nih.gov/dailymed/services/v1/ndc/{package_ndc_code}/spls.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'DATA' in data and len(data['DATA']) > 0:
            set_id = data['DATA'][0][0]
            return set_id
        else:
            return "No set_id found in the JSON."
    except requests.exceptions.RequestException as e:
        return f"Error querying DailyMed JSON: {e}"

def get_drug_info(response):
    data = response.json()
    if 'results' in data:
        result = data['results'][0]
        drug_info = {}
        openfda_fields = result.get('openfda', {})
        for field, values in openfda_fields.items():
            drug_info[field] = values[0] if values else 'N/A'
            
        for field, values in result.items():
            if field != 'openfda' and field != 'set_id' and field != 'id' and field != 'version' and field != 'effective_time':
                drug_info[field] = values[0] if values else 'N/A'
        markdown_text = convert_to_markdown(drug_info)
        chunks = split_text(markdown_text, max_tokens=4000)
        return format_with_gemini_chunks(chunks, format_with_gemini)
    else:
        print("No drug information found for this NDC code.")
        return None

def fetch_drug_info_from_openfda(ndc_code=None, brand_name=None):
    package_ndc = urllib.parse.quote(ndc_code)
    api_url = f"https://api.fda.gov/drug/label.json?search=openfda.package_ndc:\"{package_ndc}\""
    print(f"Truy vấn API OpenFDA URL: {api_url}")
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        drug_info = get_drug_info(response)
        return drug_info 
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            print("404 error encountered. Attempting to fetch set_id from DailyMed.")
            set_id = get_set_id_from_dailymed_json(ndc_code)
            print(f"Set ID từ DailyMed: {set_id}")
            if "Error" not in set_id and "No set_id" not in set_id:
                setid_api_url = f"https://api.fda.gov/drug/label.json?search=set_id:\"{set_id}\""
                print(f"Truy vấn API OpenFDA URL với set_id: {setid_api_url}")
                try:
                    response = requests.get(setid_api_url)
                    response.raise_for_status()
                    return response
                except requests.exceptions.HTTPError as setid_http_err:
                    print(f"HTTP error when querying API with set_id: {setid_http_err}")
                except Exception as e:
                    print(f"Unknown error when querying API with set_id: {e}")
            else:
                print(f"Failed to retrieve set_id from DailyMed for NDC code {ndc_code}.")
        else:
            print(f"HTTP error when querying API: {http_err}")
    except Exception as e:
        print(f"Unknown error: {e}")
    
    return None