import re


def decompose(word):
    return [hex(ord(ch)) for ch in word]


class KCC:
    # represents a Khmer Character Cluster (an indivisible string of Khmer unicode characters)


    # a complete rule:
    # bc + [bcr] + [COENG + fsc + [fscr]] + [COENG + ssc + [sscr]] + [[jnr] + dv] + [fsgn] + [ssgn] + [ZWJ + COENG + tsc]] 

    # [...] means that ... may not be present in a cluster

    # if a character isn't present then it's value is considered None

    # bc - base char 
    # bcr - bc robat/regshift  

    # fsc - first subscript character
    # fscr - fsc regshift

    # ssc - second subscript character
    # sscr - ssc regshift 

    # jnr - ZWJ or ZWNJ before dv
    # dv - dependent vowel
    # fsgn - first sign
    # ssgn - second sign

    # tsc - third subscript character

    # COENG is a constant (\u17D2) character for connecting subscripts, so it's always present if so are subscripts
    # therefore no need to store them
    # same thing with ZWJ before tsc


    # bc, fsc, ssc, tsc are all either a consonant (\u1780-\u17A2) or an independent vowel (\u17A3-\u17B3)
    # bcr, fscr, sscr are all regshifts (\u17C9-\u17CA), but bcr can also be a robat (\u17CC)
    # jnr is either a ZWJ (\u200D) or a ZWNJ (\u200C)
    #?????
    # dv is cring ngl idk hahahahahahhsduifosdfuhdsfndg;fl (\u17B6-\u17C5???) 
    # я тупа не понял, входят ли сюда символы-знаки которые после \u17C5 потому что в пдфке dv должно быть 23, а в вики 16
    # какие-то из них должны быть в dv, а какие-то в fsgn/ssgn
    # fsgn, ssgn - various signs 
    #?????






    SYMS = ["bc", "fsc", "ssc", "bcr", "fscr", "sscr", "jnr", "dv", "fsgn", "ssgn", "tsc"]
    def __init__(self, value, **kwargs):
        self.value = value
        self.hashcode = 1
        self.symbols = dict()
        for sym_name in self.SYMS:
            self.symbols[sym_name] = kwargs[sym_name] if sym_name in kwargs else None
            # hash is a product of character hashes cuz we not berry coole hehehe
            #TODO: make better hashing
            self.hashcode *= hash(kwargs[sym_name] if sym_name in kwargs else 1)
    
    def __eq__(self, other):
        #TODO: checking equality
        return self.symbols == other.symbols


    def __hash__(self):
        return self.hashcode

    def __repr__(self):
        return self.value

    def to_str(self):
        return self.__repr__()





class KCCTrieNode:
    ### a single node of KCCTrie
    # contains a single KCC and links to next KCCs (in the form of a dict kcc->link)  
    def __init__(self, kcc_value, is_terminal=False):
        self.children = dict() # dict  kcc -> trie_node
        self.kcc_value = kcc_value # kcc
        self.is_terminal = is_terminal # True means that a word ends here (a path from the root to this node is a word in the dictionary)

    # redundant?

    # def add_child(self, child_kcc, child_node):
    #     self.children += {child_kcc : child_node}

    # def search(self, target):
    #     return None if target not in self.children else self.children[target] 






class KCCTrie:
    # a Trie of KCC nodes representing the dictionary
    # a word exists in the dict if there is a path from the root node to a terminal node (and otherwise doesn't exist)
    def __init__(self):
        self.root = KCCTrieNode(None) # doesn't represent a KCC, just a workaround to create root node
        self.curr_node = None # utility link to the current node during traversal
        self.last_match = None
        
    

    # adds a word to the Trie (traverses the trie in by the provided kccs iterable creating unexistent nodes and marks the last one as terminal)
    def add_word(self, kccs):
        self.reset()
        for kcc in kccs:
            if kcc not in self.curr_node.children:
                self.curr_node.children[kcc] = KCCTrieNode(kcc)
            self.curr_node = self.curr_node.children[kcc]
        self.curr_node.is_terminal = True



    # attemps to traverse the trie by the provided kccs iterable and checks if the final node is terminal
    def match(self, kccs):
        self.reset()
        for kcc in kccs:
            if not self.test(kcc): # if this succeeds then there's no path from some character
                return False 
        return self.curr_node.is_terminal 


    # resets the search, setting curr_node to the root node
    def reset(self):
        self.curr_node = self.root
        self.words = []
        self.unrecognized = []


    # tests if there's a path from the current node to the provided node
    # if it exists switches curr_node to the next node, otherwise does nothing 
    def test(self, kcc):
        if kcc in self.curr_node.children:
            self.curr_node = self.curr_node.children[kcc]
            return True
        return False


    def ffm(self, kccs):
        start = 0 # index of a current starting cluster of the next word
        end = start # index of a current ending cluster 
        self.reset()
        lwl = 0 # length of the current longest word from `start`
        while start < len(kccs):
            if end < len(kccs) and self.test(kccs[end]): # there are dictionary words whose prefix is kccs[start:end+1] 
                end += 1
                if self.curr_node.is_terminal:
                    # kccs[start:end] is a dictionary word
                    # and it's the longest starting at kccs[start] so far, so 
                    lwl = end - start
            else:
                # no word with a prefix kccs[start:end]
                if lwl == 0:
                    # no prefix of kccs[start:] is a word in dictionary
                    # appending to unrecognized and moving the start 1 cluster forward
                    self.unrecognized.append(kccs[start])
                    start += 1 
                else:
                    # kccs[start:start+lwl] is a longest prefix of kccs[start:] that is also a dictionary word
                    # appending the word and moving the start `lwl` clusters forward
                    self.words.append(kccs[start:start + lwl])
                    start += lwl
                # returning current end to the new start                
                end = start

        # rating accuracy (amount of recognized clusters compared to unrecognized)
        self.accuracy = 1 - len(self.unrecognized) / len(kccs)

    def print_accuracy(self):
        print(f"accuracy: {self.accuracy}")

    def print_results(self):
        print(f"accuracy: {self.accuracy}")
        print(f"recongized:{self.words}")
        print(f"unrecongized:{self.unrecognized}")
        
            





class KCCParser:
    # parses a string into KCCs
    def __init__(self, text):
        self.text = text.replace(u"\u200B", "") # removing zero width spaces
        self.end = 0 # next char following previous cluster 
        self.clusters = []
        self.MAX_LENGTH = 15
        self.make_regex()



    def make_regex(self):
        r_con = r"[\u1780-\u17A2]"
        r_ind = r"[\u17A3-\u17B3]"
        r_robat = r"\u17CC"
        r_shift = r"[\u17C9\u17CA]"
        r_dep = r"[\u17B6-\u17C5]" # ????
        r_zwnj = r"\u200C"
        r_zwj = r"\u200D"
        r_sgn = r"[\u17C6-\u17DD]" # ???
        r_coeng = r"\u17D2"

        r_c = f"{r_con}|{r_ind}"
        r_jnr = f"{r_zwnj}|{r_zwj}"


        r_base = f"(?P<bc>{r_c})(?P<bcr>{r_robat}|{r_shift})?"
        r_fsc = f"{r_coeng}(?P<fsc>{r_c})(?P<fscr>{r_shift})?"
        r_ssc = f"{r_coeng}(?P<ssc>{r_c})(?P<sscr>{r_shift})?"
        r_dv = f"(?P<jnr>{r_jnr})?(?P<dv1>{r_dep})"
        r_lsub = f"{r_zwj}{r_coeng}(?P<tsc>{r_c})"
        r_right = f"({r_dv})?(?P<fsgn>{r_sgn})?(?P<ssgn>{r_sgn})?({r_lsub})?"

        r_kcc = f"({r_base})({r_fsc})?({r_ssc})?({r_right})"

        self.kcc_reg = re.compile(r_kcc)
        



    # parses the next portion of the provided string into a cluster
    def next_cluster(self):
        if self.end >= len(self.text):
            return False
        portion = self.text[self.end:self.end + self.MAX_LENGTH]
        match = self.kcc_reg.match(portion)
        if match == None:
            self.last_end = len(self.text)
            raise RuntimeError(f"malwared word:{self.text}, dec={decompose(self.text)}")
        self.clusters.append(KCC(match.group(0), **match.groupdict()))
        self.end = self.end + match.end()
        if match.end() == 0:
            print("jeroma ti debs")
            exit(1)
        return True
        



    def to_clusters(self):
        while self.next_cluster():
            pass
        return self.clusters


    # utility funciton for expecting different kinds of characters
    # returns the character if it matches expectations and shifts the current end to the next char
    # otherwise does nothing
    def test(self, *predicates):
        if any(predicate() for predicate in predicates):
            c = self.text[self.end]
            self.end += 1
            return c
        return None



        






#препроцессинг
dictionary = open("names_copy", encoding="utf-8")

clustered = dict()
for i, line in enumerate(dictionary):
    if "malwared" in line:
        print(f"skipping malwared line|{line}|")
        continue
    word = line.strip()
    try:
        clustered[word] = KCCParser(word).to_clusters()
    except RuntimeError:
        print(f"skipping malwared word:|{word}|")
        print(f"in line {i}")



forward_tree = KCCTrie() 
backward_tree = KCCTrie()

for w, c in clustered.items():
    forward_tree.add_word(c)
    backward_tree.add_word(reversed(c))




# сама таска
textfile = open("text", encoding="utf-8")

seg_task = textfile.readline()

clustered_seg_task = KCCParser(seg_task).to_clusters()

forward_tree.ffm(clustered_seg_task)
forward_tree.print_accuracy()

backward_tree.ffm(clustered_seg_task[::-1])
backward_tree.print_accuracy()




out_file = open("text_out", "w")


if (forward_tree.accuracy > backward_tree.accuracy):
    segmentation = forward_tree.words
    for word in forward_tree.words:
        out_file.write("".join(kcc.to_str() for kcc in word) + "_")
else:
    for word in backward_tree.words[::-1]:
        out_file.write("".join([kcc.to_str() for kcc in word][::-1]) + "_")






