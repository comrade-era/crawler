import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import time
import concurrent.futures
import nltk
import spacy
from transformers import pipeline
import torch 

# Load spaCy for keyword extraction
nlp = spacy.load("en_core_web_sm")

# Initialize Hugging Face transformer pipeline for summarization or heading generation
summarizer = pipeline("summarization")

# Keywords to filter relevant URLs
KEYWORDS = [
    "Cyber incident", "Cyber attack", "Cyber", "Security threat", "Data breach",
    "Hacking attempt", "Phishing attack", "Ransomware", "Malware", "Virus outbreak",
    "Banking cyber attack", "Financial data breach", "Healthcare data breach",
    "Hospital cyber attack", "Power grid hacking", "Energy sector cyber threat",
    "Government website hack", "Public service cyber incident",
    "Distributed Denial of Service", "Zero-day", "SQL injection", "Cross-site scripting",
    "Man-in-the-middle attack", "Advanced persistent threat", "Security alert",
    "Cybersecurity update", "Incident report", "Security advisory", "Cyber threat bulletin",
    "Insider threat", "State-sponsored attack", "Cyber espionage", "Hacktivist",
    "Cybercriminal group", "Artificial-intelligence-powered cyber-attack",
    "Deep fake phishing", "Cloud security breach", "IoT device hacking"
]

# Function to check if URL is relevant based on keywords
def is_relevant_url(url):
    return any(keyword.lower() in url.lower() for keyword in KEYWORDS)

# Function to extract a topic-based heading
def generate_heading(text):
    doc = nlp(text)
    # Extract the most common noun phrases for the heading
    noun_phrases = [chunk.text for chunk in doc.noun_chunks]
    return " ".join(noun_phrases[:3])  # Take the first few noun phrases for a relevant heading

# Function to summarize content using Sumy
def summarize_text(content):
    parser = PlaintextParser.from_string(content, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 2)  # Summarize to 2 sentences
    return " ".join(str(sentence) for sentence in summary)

# Function to scrape and summarize relevant URLs
def scrape_and_summarize(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Get main content for summarization
        paragraphs = soup.find_all("p")
        content = " ".join([p.get_text() for p in paragraphs])

        if content:
            # Generate heading and summary
            heading = generate_heading(content)
            summary = summarize_text(content)
            
            # Print the heading and the summary
            print(f"Heading: {heading}\nSummary: {summary}\n")
    except Exception as e:
        print(f"Error scraping {url}: {e}")

# Recursive function to crawl URLs
def crawl(url, visited_urls, depth=0, max_depth=2):
    if depth > max_depth or url in visited_urls:
        return
    
    visited_urls.add(url)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all hyperlinks
        for link in soup.find_all("a", href=True):
            link_url = urljoin(url, link["href"])
            parsed_url = urlparse(link_url)

            # Process only valid HTTP/HTTPS URLs
            if parsed_url.scheme in ["http", "https"]:
                if is_relevant_url(link_url):
                    scrape_and_summarize(link_url)

                # Crawl deeper if within the allowed depth
                crawl(link_url, visited_urls, depth + 1, max_depth)

    except Exception as e:
        print(f"Error crawling {url}: {e}")

def main(seeds):
    while True:
        visited_urls = set()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for seed in seeds:
                executor.submit(crawl, seed, visited_urls)
        
        print("Waiting 15 minutes before the next crawl cycle...\n")
        time.sleep(900)  

seed_urls = [
    "https://thehackernews.com",
    "https://www.securityweek.com/",
    "https://www.securityweek.com/",
    "https://social.cyware.com/cyber-security-news-articles",
    "https://www.wired.com/tag/cybersecurity/",
    "https://www.securitymagazine.com/topics/2236-cybersecurity-news",
    "https://www.bbc.com/news/topics/cz4pr2gd85qt",
    "https://us-cert.cisa.gov/ncas",
    "https://nvd.nist.gov/",
    "https://infosecwriteups.com/",
    "https://thehill.com/policy/cybersecurity",
    "https://techrepublic.com/article/what-is-cybersecurity-and-why-is-it-important/",
    "https://theinformation.com/articles",
    "https://thehackernews.com/search/label/Cyber%20Attack",
    "https://timesofindia.indiatimes.com/topic/cybersecurity",
    "https://economictimes.indiatimes.com/news/cybersecurity",
    "https://hindustantimes.com/",
    "https://bbc.com/news/technology",
    "https://cnn.com/business/tech",
    "https://forbes.com/cybersecurity/",
    "https://zdnet.com/topic/security/",
    "https://cnet.com/topics/security/",
    "https://securityweek.com/",
    "https://darkreading.com/",
    "https://infosecurity-magazine.com/",
    "https://cybersecurityinsiders.com/",
    "https://krebsonsecurity.com/",
    "https://threatpost.com/",
    "https://scmagazine.com/",
    "https://techcrunch.com/tag/cybersecurity/",
    "https://wired.com/category/security/",
    "https://bloomberg.com/technology",
    "https://reuters.com/technology",
    "https://govinfosecurity.com/",
    "https://csoonline.com/",
    "https://us-cert.cisa.gov/",
    "https://securityaffairs.co/",
    "https://blog.malwarebytes.com/",
    "https://www.paloaltonetworks.com/blog",
    "https://fortiguard.com/",
    "https://www.fireeye.com/blog.html",
    "https://www.symantec.com/blogs/",
    "https://www.bitdefender.com/blogs/",
    "https://www.securityintelligence.com/",
    "https://cloudsecurityalliance.org/",
    "https://arstechnica.com/information-technology/",
    "https://venturebeat.com/security/",
    "https://www.techradar.com/news/security",
    "https://www.hackerone.com/blog",
    "https://privacynews.com/",
    "https://threathunting.net/",
    "https://www.theregister.com/security/",
    "https://securosis.com/",
    "https://www.beyondtrust.com/blog",
    "https://www.trendmicro.com/en_us/research.html",
    "https://cybereason.com/blog/",
    "https://varonis.com/blog/",
    "https://www.knowbe4.com/blog",
    "https://www.cyberark.com/resources/blog/",
    "https://blog.checkpoint.com/",
    "https://www.dell.com/en-us/security",
    "https://www.troyhunt.com/",
    "https://www.f-secure.com/weblog",
    "https://www.sophos.com/en-us/blogs",
    "https://dzone.com/security",
    "https://cylance.com/blog/",
    "https://crowdstrike.com/blog/",
    "https://resilience.com/blog/",
    "https://blog.avast.com/cybersecurity",
    "https://netmagazine.com/news/security",
    "https://infosec-journal.com/",
    "https://www.sciencedirect.com/topics/computer-science/cyber-security",
    "https://informationweek.com/security",
    "https://www.helpnetsecurity.com/",
    "https://darknetdiaries.com/",
    "https://www.cio.com/article/cybersecurity",
    "https://www.technologyreview.com/security/"
]


main(seed_urls)
