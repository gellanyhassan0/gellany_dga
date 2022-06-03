import pickle
import tldextract
import argparse
import json
import math
import re

class dga_inspector():
    
# init method or constructor
    def __init__(self, domain = None, pki = None):

                          
                          self.pki = pki
                          self.domain = domain
          
    def read_file(filename):
        with open(filename) as f:
            for line in f:
                yield line.strip("\n")


    def domain_check(domain):
        # skip tor domains
        if domain.endswith(".onion"):
            print("Tor domains is ignored...")
            return
        # we only interested in main domain name without subdomain and tld
        domain_without_sub = tldextract.extract(domain).domain
        # skip localized domains
        if domain_without_sub.startswith("xn-"):
            print("Localized domains is ignored...")
            return
        # skip short domains
        if len(domain_without_sub) < 6:
            print("Short domains is ignored...")
            return
        domain_entropy = entropy(domain_without_sub)
        domain_consonants = count_consonants(domain_without_sub)
        domain_length = len(domain_without_sub)
        return domain_without_sub, domain_entropy, domain_consonants, domain_length


    
                                            
                                              
    def entropy(string):
                    """
                    Calculates the Shannon entropy of a string
                    """

                    # get probability of chars in string
                    prob = [ float(string.count(c)) / len(string) for c in dict.fromkeys(list(string)) ]

                    # calculate the entropy
                    entropy = - sum([ p * math.log(p) / math.log(2.0) for p in prob ])

                    return entropy


    def count_consonants(string):
                    """
                    Counting consonants in a string
                    """
                    consonants = re.compile("[bcdfghjklmnpqrstvwxyz]")
                    count = consonants.findall(string)
                    return len(count)

    def gib_detect(self):
        
                    model_data = pickle.load(open('gib_model.pki', 'rb'))

                    while True:
                                l = input()
                                model_mat = model_data['mat']
                                threshold = model_data['thresh']
                                print(gib_detect_train.avg_transition_prob(l, model_mat) > threshold)   
                                
                                
    def normalize(line):
                    """ Return only the subset of chars from accepted_chars.
                    This helps keep the  model relatively small by ignoring punctuation, 
                    infrequenty symbols, etc. """
                    return [c.lower() for c in line if c.lower() in accepted_chars]

    def ngram(n, l):
        """ Return all n grams from l after normalizing """
        filtered = normalize(l)
        for start in range(0, len(filtered) - n + 1):
            yield ''.join(filtered[start:start + n])

    def train():
        """ Write a simple model as a pickle file """
        k = len(accepted_chars)
        # Assume we have seen 10 of each character pair.  This acts as a kind of
        # prior or smoothing factor.  This way, if we see a character transition
        # live that we've never observed in the past, we won't assume the entire
        # string has 0 probability.
        counts = [[10 for i in range(k)] for i in range(k)]

        # Count transitions from big text file, taken 
        # from http://norvig.com/spell-correct.html
        for line in open('big.txt'):
            for a, b in ngram(2, line):
                counts[pos[a]][pos[b]] += 1

        # Normalize the counts so that they become log probabilities.  
        # We use log probabilities rather than straight probabilities to avoid
        # numeric underflow issues with long texts.
        # This contains a justification:
        # http://squarecog.wordpress.com/2009/01/10/dealing-with-underflow-in-joint-probability-calculations/
        for i, row in enumerate(counts):
            s = float(sum(row))
            for j in range(len(row)):
                row[j] = math.log(row[j] / s)

        # Find the probability of generating a few arbitrarily choosen good and
        # bad phrases.
        good_probs = [avg_transition_prob(l, counts) for l in open('good.txt')]
        bad_probs = [avg_transition_prob(l, counts) for l in open('bad.txt')]

        # Assert that we actually are capable of detecting the junk.
        assert min(good_probs) > max(bad_probs)

        # And pick a threshold halfway between the worst good and best bad inputs.
        thresh = (min(good_probs) + max(bad_probs)) / 2
        pickle.dump({'mat': counts, 'thresh': thresh}, open('gib_model.pki', 'wb'))

    def avg_transition_prob(l, log_prob_mat):
        """ Return the average transition prob from l through log_prob_mat. """
        log_prob = 0.0
        transition_ct = 0
        for a, b in ngram(2, l):
            log_prob += log_prob_mat[pos[a]][pos[b]]
            transition_ct += 1
        # The exponentiation translates from log probs to probs.
        return math.exp(log_prob / (transition_ct or 1))                            



def main():

    accepted_chars = 'abcdefghijklmnopqrstuvwxyz '
    pos = dict([(char, idx) for idx, char in enumerate(accepted_chars)]) 
    parser = argparse.ArgumentParser(description="DGA domain detection")
    parser.add_argument("-d", "--domain", help="Domain to check")
    parser.add_argument("-f", "--file", help="File with domains. One per line")
    parser.add_argument("-fp", "--file_pki", help="File with domains. One per line")
    args = parser.parse_args()
    model_data = pickle.load(open(args.file_pki, 'rb'))
    model_mat = model_data['mat']
    threshold = model_data['thresh']
    
    if args.domain:
        if dga_inspector(domain = args.domain).domain_check():
            domain_without_sub, domain_entropy, domain_consonants, domain_length = dga_inspector(domain = args.domain).domain_check()
            print("Analysing domain...")
            if domain_entropy > 3.8:
                print("High entropy(>3.8) is a strong indicator of DGA domain.\n"
                      "This domain scored: %d" % domain_entropy)
            if domain_consonants > 7:
                print("High consonants(>7) count is an indicator of DGA domain\n"
                      "This domain scored: %d" % domain_consonants)
            if domain_length > 12:
                print("Long domain name(>12) can also indicate DGA\n"
                      "This domain scored: %d" % domain_length)
            if not gib_detect_train.avg_transition_prob(domain_without_sub, model_mat) > threshold:
                print("Domain %s is DGA!" % args.domain)
            else:
                print("Domain %s is not DGA! Probably safe :)\n"
                      "Don't quote me on that though\n"
                      "Additional information: \n"
                      "Entropy: %d\n"
                      "Consonants count: %d\n"
                      "Name length: %d" % (args.domain, domain_entropy, domain_consonants, domain_length))
    elif args.file:
        domains = read_file(args.file)
        results = {"domain": "", "is_dga": "", "high_consonants": "", "high_entropy": "", "long_domain": ""}
        with open("dga_domains.json", "w") as f:
            for domain in domains:
                print("Working on %s" % domain)
                results["domain"] = domain
                if domain_check(domain):
                    domain_without_sub, domain_entropy, domain_consonants, domain_length = domain_check(domain)
                    if domain_entropy > 3.8:
                        results["high_entropy"] = domain_entropy
                    elif domain_consonants > 7:
                        results["high_consonants"] = domain_consonants
                    elif domain_length > 12:
                        results["long_domain"] = domain_length
                    if not gib_detect_train.avg_transition_prob(domain_without_sub, model_mat) > threshold:
                        results["is_dga"] = True
                    else:
                        results["is_dga"] = False
                json.dump(results, f, indent=4)
        print("File dga_domains.json is created")    
            
      
main()

