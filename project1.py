import nltk
from bs4 import BeautifulSoup
import glob


# read all the files
def load_file(file_directory):
    f = open(file_directory, "r", encoding="iso8859_2")
    data = f.read()
    f.close()
    soup = BeautifulSoup(data, "html.parser")
    documents = soup.find_all("reuters")
    return documents


# clean documents [ ["newid", "....."], [],...]
def clean_file(file_directory):
    new_documents = []
    for document in file_directory:
        sub_document = []
        if document["newid"] is not None:
            sub_document.append(document["newid"])
        else:
            sub_document.append(None)
        if document.body is not None:
            sub_document.append(document.body.text)
        else:
            sub_document.append("")
        new_documents.append(sub_document)
    return new_documents


# tokenize that text in the sub_documents
def tokenize_text(text):
    tokens = nltk.word_tokenize(text)
    tokens = [token.lower() for token in tokens]
    wnl = nltk.WordNetLemmatizer()
    tokens = [wnl.lemmatize(t) for t in tokens]
    return tokens


# spimi algorithm
def spimi(dictionary, sub_document):
    for token in sub_document[1]:
        if dictionary.get(token, None) is not None:
            dictionary[token].add(str(sub_document[0]))
        else:
            dictionary[token] = set([str(sub_document[0])])


# write memory to txt file
def save_memorydata_to_txt(dictionary, f_name):
    f = open(f_name, "w")
    for key in sorted(dictionary.keys()):
        f.write(key + ":" + " ".join(dictionary.get(key)) + "\n")
    f.close()


# read txt file
def read_line_from_txt(block_file, block_number):
    first_line = block_file.readline()
    key_value_pair = first_line.split(":")
    return {key_value_pair[0]: [block_number, key_value_pair[1].split(" ")]}


files = glob.glob("./reuters21578/*reut2*.sgm")
#print(len(files))

dictionary = {}
block_number = 1

for file in files:
    documents = load_file(file)
    print(file)
    clean_documents = clean_file(documents)
    counter = 0

    for document in clean_documents:
        document[1] = tokenize_text(document[1])

    for document in clean_documents:
        spimi(dictionary, document)
        counter += 1
        if counter == 500:
            counter = 0
            save_memorydata_to_txt(dictionary, "./blocks/block" + str(block_number) + ".txt")
            dictionary = {}
            block_number += 1
            print(block_number)

