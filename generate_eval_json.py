import json
import os
import random
import time
import ollama
from tqdm import tqdm
import crawler


def generate_filter_code(input, data):
    # get data from crawler
    if not data or not input:
        raise ValueError("No data or input provided.")
    
    # parse data to extract information for the prompt


if __name__ == "__main__":
   
    data = crawler.get_info_service()
    print("Scrivi la descrizione del servizio che vuoi cercare in linguaggio naturale (max 200 caratteri):")
    input = input.lower()
    if len(input) > 200:
        raise ValueError("Input exceeds maximum length of 200 characters.")
    generate_filter_code(input, data)
