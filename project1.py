import nltk
from bs4 import BeautifulSoup
import glob
from collections import OrderedDict
import re
from nltk.corpus import stopwords

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
    # 1)unfiltered
    tokens = nltk.word_tokenize(text)

    # 2)no numbers
    tokens = [re.sub(r'[^\w\s]', '', token) for token in tokens]
    tokens = [re.sub(r'\d+', '', token) for token in tokens]

    # 3)case folding
    tokens = [token.lower() for token in tokens]

    # 4) 30 stop words
    stop_word = stopwords.words("english")
    tokens = [token for token in tokens if token not in stop_word[:30]]

    # 5) 150 stop words
    stop_word = stopwords.words("english")
    tokens = [token for token in tokens if token not in stop_word[:150]]
    return tokens

# read txt file
def read_line_from_txt(block_file, block_number):
    first_line = block_file.readline()
    key_value_pair = first_line.split(":")
    return [key_value_pair[0], [block_number, key_value_pair[1].split(" ")]]


# spimi algorithm
def spimi(dictionary, sub_document):
    for token in sub_document[1]:
        if dictionary.get(token, None) is not None:
            dictionary[token].add(str(sub_document[0]))
        else:
            dictionary[token] = set([str(sub_document[0])])


# merge blocks
def merge_blocks(block_files):
    def sorted_as_int(nums):
        nums = [int(num) for num in nums if len(re.findall(r"^\d+$", num.lstrip("\n"))) > 0]
        nums = sorted(nums)
        nums = [str(num) for num in nums]
        return nums

    # initialize the index file
    file_output = "./indexs/index{}.txt"
    file_count = 0
    f = open(file_output.format(file_count), "w")
    count = 0

    posting_list_length = 0

    files = [i for i in range(len(block_files))]  # this is the block numbers range
    for file_name in block_files:
        index = int(re.findall(r"\d+", file_name)[0])
        files[index] = open(file_name, "r")

    lines = {}  # working space
    for i in range(len(files)):
        try:
            line = read_line_from_txt(files[i], i)    # read first line
        except IndexError:
            continue
        if line == " ":
            files[i].close()   # if there is nothing in the line, the close it
        else:
            if lines.get(line[0], None) is not None:
                lines[line[0]].append(line[1])
            else:
                lines[line[0]] = [line[1]]

    while len(lines.keys()) > 0:    # [key, [index[value1,value2,... ]] ]
        token = sorted(lines.keys())[0]   # key
        index_value = [value[0] for value in lines.get(token)]  # index
        postings = [value[1] for value in lines.get(token)]    # [ [value1, value2, ...] [value1, value2, ...] ]

        lists = []
        for posting in postings:
            lists.extend(posting)

        lists = sorted_as_int(list(set(lists)))    # p is integer string in ascending order

        f.write(str(token) + ":" + " ".join(lists) + "\n")
        count += 1
        posting_list_length += len(lists)
        if count == 25000:
            f.close()
            file_count += 1
            f = open(file_output.format(file_count), "w")
            count = 0
        del lines[token]

        # these are touched files
        for index in index_value:
            try:
                line = read_line_from_txt(files[index], index)  # here index is the block number
            except IndexError:
                continue
            if line == " ":
                files[index].close()
            else:
                if lines.get(line[0], None) is not None:
                    lines[line[0]].append(line[1])
                else:
                    lines[line[0]] = [line[1]]
    f.close()
    return (file_count * 25000 + count, posting_list_length)



# write memory to txt file
def save_memorydata_to_txt(dictionary, f_name):
    f = open(f_name, "w")
    for key in sorted(dictionary.keys()):
        f.write(key + ":" + " ".join(sorted(dictionary.get(key))) + "\n")
    f.close()


# query: intersection
def query_intersection(file: str, words: list):
    f = open(file, "r")
    result = []

    if len(words) == 0:
        return result

    a = words[0]
    line = f.readline()

    while line != '':
        if line.split(":")[0] == a:
            result = line.split(":")[1].split(" ")
            break
        else:
            line = f.readline()

    b_listing = []
    for i in range(1, len(words)):
        b = words[i]
        line = f.readline()
        while line != '':
            if line.split(":")[0] == b:
                b_listing = line.split(":")[1].split(" ")
                break
            else:
                line = f.readline()
        result = intersection(result, b_listing)
    f.close()
    return result


def intersection(a, b):
    result = []
    i = 0
    j = 0
    while i < len(a) and j < len(b):
        if int(a[i]) == int(b[j]):
            result.append((a[i].rstrip("\n")))
            i += 1
            j += 1
        elif int(a[i]) < int(b[j]):
            i += 1
        else:
            j += 1
    return result


# query: union
def query_union(file: str, words: list):
    f = open(file, "r")
    result = []

    if len(words) == 0:
        return result

    a = words[0]
    line = f.readline()

    while line != '':
        if line.split(":")[0] == a:
            result = line.split(":")[1].split(" ")
            break
        else:
            line = f.readline()

    b_listing = []
    for i in range(1, len(words)):
        b = words[i]
        line = f.readline()
        while line != '':
            if line.split(":")[0] == b:
                b_listing = line.split(":")[1].split(" ")
                break
            else:
                line = f.readline()
        result = union(result, b_listing)
    f.close()
    return result


def union(a, b):
    result = []
    i = 0
    j = 0
    while i < len(a) and j < len(b):
        if int(a[i]) < int(b[j]):
            result.append((a[i].rstrip("\n")))
            i += 1
        elif int(a[i]) > int(b[j]):
            result.append((b[j].rstrip("\n")))
            j += 1
        else:
            result.append((b[j].rstrip("\n")))
            j += 1

# Print remaining elements of the larger array
    while i < len(a):
        result.append(a[i].rstrip("\n"))
        i += 1

    while j < len(b):
        result.append(b[j].rstrip("\n"))
        j += 1

    # add frequency to each list element
    list_with_frequency = {x: result.count(x) for x in result}

    # order list according to list value frequency in descending manner
    ordered_list = OrderedDict(sorted(list_with_frequency.items(), key=lambda x: x[1], reverse=True))

    return list(ordered_list.keys())


# # read files to generate blocks
# files = sorted(glob.glob("./reuters21578/*reut2*.sgm"))
# #print(len(files))
#
# dictionary = {}
# block_number = 0
#
# for file in files:
#     documents = load_file(file)
#     print(file)
#     clean_documents = clean_file(documents)
#     counter = 0
#
#     for document in clean_documents:
#         document[1] = tokenize_text(document[1])
#
#     for document in clean_documents:
#         spimi(dictionary, document)
#         counter += 1
#         if counter == 500:
#             counter = 0
#             save_memorydata_to_txt(dictionary, "./blocks/block" + str(block_number) + ".txt")
#             dictionary = {}
#             block_number += 1
#             print(block_number)
#
#
# files = glob.glob("./blocks/*.txt")
# print("start")
# size, posting_list_size = merge_blocks(files)
# print("term size", size, "posting list size", posting_list_size)



query = "Jimmy Carter"
result = query_intersection("./indexs/index0.txt",sorted(tokenize_text(query)))
if len(result) == 0:
    result = query_intersection("./indexs/index1.txt", tokenize_text(query))
print("intersection", result)



#
# result2 = query_union("./blocks/block36.txt", tokenize_text(query))
# print("union", result2)
# print(len(result2))
