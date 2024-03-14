
class InvertedIndex:
    def __init__(self, index_file_path, postings_file_path):
        self.index = self.load_index(index_file_path)
        self.postings = self.load_postings(postings_file_path)

    def load_index(self, index_file_path):
        with open(index_file_path, 'r', encoding='utf-8') as index_file:
            index_data = {}
            for line in index_file:
                term_id, term, doc_frequency = line.strip().split(':')
                index_data[int(term_id)] = {
                    'term': term,
                    'doc_frequency': int(doc_frequency)
                }
            return index_data

    def load_postings(self, postings_file_path):
        postings_data = {}
        current_term_id = None

        with open(postings_file_path, 'r', encoding='utf-8') as postings_file:
            for line in postings_file:
                if line.strip():  # Skip empty lines
                    if line.endswith(":") or line.endswith(':\n'):
                        current_term_id = int(line.strip()[:-1])
                        postings_data[current_term_id] = []
                    else:
                        # Extract doc_id and positions from the line
                        parts = line.split(':')
                        doc_id = int(parts[0].strip())
                        positions_str = parts[1].strip()
                        
                        # Check for '[' at the beginning and ']' at the end
                        if positions_str.startswith('[') and positions_str.endswith(']'):
                            positions_str = positions_str[1:-1]  # Remove brackets
                            positions = [int(pos.strip()) for pos in positions_str.split(',')]
                            postings_data[current_term_id].append((doc_id, positions))

        return postings_data

    def search_terms(self, terms, index_file_path, postings_file_path):
            index_data = self.load_index(index_file_path)
            postings_data = self.load_postings(postings_file_path)

            for term in terms:
                term_id = None

                for current_term_id, data in index_data.items():
                    if data['term'] == term:
                        term_id = current_term_id
                        break

                if term_id is not None:
                    if term_id in postings_data:
                        print(f"Postings for '{term}':")
                        for doc_id, positions in postings_data[term_id]:
                            print(f"  DocID: {doc_id}, Positions: {positions}")
                    else:
                        print(f"No postings found for the term '{term}'.")
                else:
                    print(f"Term '{term}' not found in the index.")


index_file_path = "index.txt"
postings_file_path = "postings.txt"
index = InvertedIndex(index_file_path, postings_file_path)
user_input = input("Enter a sequence of single terms (separated by space): ")
search_terms = user_input.split()
index.search_terms(search_terms, index_file_path, postings_file_path)
