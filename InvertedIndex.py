import os
import re
import json
from collections import defaultdict
from functools import cmp_to_key

class Node:
    def __init__(self, doc_id, positions):
        self.doc_id = doc_id
        self.positions = positions
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, doc_id, positions):
        new_node = Node(doc_id, positions)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

class InvertedIndex:
    def __init__(self):
        self.term_list = []
        self.postings = defaultdict(LinkedList)
        self.doc_frequency = defaultdict(int)
        self.term_id = 0
    def add_term(self, term, doc_id, position):


        if term not in [t[1] for t in self.term_list]:
            self.term_id += 1
            self.term_list.append((self.term_id,term))
            self.term_list.sort(key = lambda x: x[1])
            

        posting_list = self.postings[term]
        posting_node = posting_list.head

        while posting_node:
            if posting_node.doc_id == doc_id:
                # If doc_id is already present, append the position to the existing list of positions
                posting_node.positions.append(position)
                return
            posting_node = posting_node.next

        # If doc_id is not present, add a new node with a list of positions
        posting_list.append(doc_id, [position])
        self.doc_frequency[term] += 1

    def write_index(self, index_file_path, stop_words):
        with open(index_file_path, 'w', encoding='utf-8') as index_file:
            # Write the sorted list of terms with document frequency and link to postings
            for term_id, term in sorted(self.term_list, key=lambda x: x[1]):
                if term not in stop_words:
                    index_file.write(f"{term_id}:{term}: {self.doc_frequency[term]}\n")
    
    def write_postings(self, postings_file_path, stop_words):
        with open(postings_file_path, 'w', encoding='utf-8') as postings_file:
            for term_id, term in sorted(self.term_list, key=lambda x: x[1]):
                if term not in stop_words:
                    postings_file.write(f"{term_id}:\n")
                    # postings_file.write(f"{term}:\n")
                    posting_node = self.postings[term].head

                    while posting_node:
                        postings_file.write(f"  {posting_node.doc_id}: {posting_node.positions}\n")
                        posting_node = posting_node.next

def remove_control_characters(text):
    control_characters = {
        0x202C: None,  
        0x202B: None,  
        0x200A: None,  
        0x202A: None,  
        0x0651: None,  # ARABIC SHADDA
        0x060C: None,  # ARABIC COMMA
        0x060D: None,  # ARABIC DATE SEPARATOR
        0x060E: None,  # ARABIC POETIC VERSE SIGN
        0x060F: None,  # ARABIC SIGN MISRA
        0x061B: None,  # ARABIC SEMICOLON
        0x061E: None,  # ARABIC TRIPLE DOT PUNCTUATION MARK
        0x061F: None,  # ARABIC QUESTION MARK
        0x066D: None,  # ARABIC FIVE POINTED STAR
        0x06D4: None,  # ARABIC FULL STOP
        0x06DD: None,  # ARABIC END OF AYAH
        0x06DE: None,  # ARABIC START OF RUB EL HIZB
        0x06E9: None,  # ARABIC PLACE OF SAJDAH
        0x06FD: None,  # ARABIC SIGN SINDHI AMPERSAND
        0xFD3E: None,  # Arabic ornate left parenthesis
        0xFD3F: None,  # Arabic ornate right parenthesis
        0xFEFF: None,  # ZERO WIDTH NO-BREAK SPACE
        0x0651: None   # ARABIC SHADDA
    }

    translation_table = str.maketrans(control_characters)
    cleaned_text = text.translate(translation_table)

    return cleaned_text

def remove_diacritics(word):
    diacritic_marks = ['ّ', 'َ', 'ِ', 'ُ', 'ً', 'ٍ', 'ٌ', 'ٓ', 'ٰ', 'ٖ', 'ٗ', 'ٚ', 'ٖ', 'ٗ', 'ٚ', 'ۖ', 'ۗ', 'ۘ', 'ۙ', 'ۚ', 'ۛ', 'ۜ', '۟', '۠','ء' ,'(', ')', '"', ',',' ؑ','\'']
    return ''.join(char for char in word if char not in diacritic_marks)

def remove_diacritics_from_list(urdu_words):
    return [remove_diacritics(word) for word in urdu_words]

def contains_english_character(word):
    return any(0x0000 <= ord(char) <= 0x007F for char in word)


def remove_numbers(urdu_words):
    return [word for word in urdu_words if not word.isdigit()]

def remove_english_numbers(text):
    cleaned_text = re.sub(r'\b\d+\b', '', text)
    return cleaned_text.strip()

def remove_english_words(urdu_words):
    return [word for word in urdu_words if not contains_english_character(word)]
def load_stop_words(stop_words_file):
    
    with open(stop_words_file, 'r', encoding='utf-8') as f:
        urdu_stop_words = f.read().strip().split()
        cleaned_urdu_words = [remove_control_characters(word) for word in urdu_stop_words]
        stop_words = remove_english_words(cleaned_urdu_words)
        stop_words = remove_diacritics_from_list(stop_words)
        stop_words = [word for word in stop_words if word] # Remove empty strings
        return stop_words
    

def process_corpus(corpus_folder, stop_words):
    inverted_index = InvertedIndex()
    docid = 0
    for root, dirs, files in os.walk(corpus_folder):
        for file in files:
            docid += 1 
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tokens = content.strip().split()
                tokens = [remove_control_characters(word) for word in tokens]
                tokens = remove_diacritics_from_list(tokens)
                tokens = [word for word in tokens if word] # Remove empty strings
                tokens = remove_numbers(tokens)
                tokens = [remove_english_numbers(word) for word in tokens]
                for position, token in enumerate(tokens, start=1):
                    if token.strip() not in stop_words:
                        inverted_index.add_term(token,  docid, position)
    return inverted_index

def print_stop_words_to_file(stop_words, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for word in stop_words:
            output_file.write(f"{word}\n")

corpus_folder = "Urdu Corpus"
stop_words_file = "Closed Class Word List.txt"
index_file_path = "index.txt"
postings_file_path = "postings.txt"
stop_words = load_stop_words(stop_words_file)
print_stop_words_to_file(stop_words, "CheckStopWords.txt")
index = process_corpus(corpus_folder, stop_words)
index.write_index(index_file_path, stop_words)
index.write_postings(postings_file_path, stop_words)