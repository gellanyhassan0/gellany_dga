import pickle
import tldextract
import argparse
import json
import math
import re

class dga_inspector():
    
    def __init__(self, domain = None, filename= None, string = None, log_prob_mat=None, model_data=None, model_mat = None):

                       self.domain = domain
                       self.filename = filename   
                       self.string = string
                       self.log_prob_mat = log_prob_mat
                       self.model_data = model_data
                       self.model_mat = model_mat
                       
                          

    def read_file(self):
        with open(self.filename) as f:
            for line in f:
                yield line.strip("\n") 

    def domain_check(self):
            # skip tor domains
            if self.domain.endswith(".onion"):
                print("Tor domains is ignored...")
                return
            # we only interested in main domain name without subdomain and tld
            global domain_without_sub
            domain_without_sub = tldextract.extract(self.domain).domain
            #print("domain_without_sub", domain_without_sub)
            # skip localized domains
            if domain_without_sub.startswith("xn-"):
                #print("Localized domains is ignored...")
                return
            # skip short domains
            if len(domain_without_sub) < 6:
                #print("Short domains is ignored...")
                return
            global domain_entropy
            domain_entropy = dga_inspector(string = domain_without_sub).entropy()
            #print("domain_entropy", domain_entropy)
            global domain_consonants
            domain_consonants = dga_inspector(string = domain_without_sub).count_consonants()
            #print(domain_consonants)
            global domain_length
            domain_length = len(domain_without_sub)
            #print("domain_length",domain_length)
            #print(domain_without_sub, domain_entropy, domain_consonants, domain_length)
            return domain_without_sub, domain_entropy, domain_consonants, domain_length
            

    def entropy(self):
                    """
                    Calculates the Shannon entropy of a string
                    """

                    # get probability of chars in string
                    prob = [ float(self.string.count(c)) / len(self.string) for c in dict.fromkeys(list(self.string)) ]

                    # calculate the entropy
                    entropy = - sum([ p * math.log(p) / math.log(2.0) for p in prob ])

                    return entropy        

    def count_consonants(self):
                    """
                    Counting consonants in a string
                    """
                    consonants = re.compile("[bcdfghjklmnpqrstvwxyz]")
                    count = consonants.findall(self.string)
                    return len(count)

    def entropy_check(self):
                  
                    if domain_entropy > 3.8:
                           print("High entropy(>3.8) is a strong indicator of DGA domain.\n" "This domain scored: %d" % domain_entropy)
                    if domain_consonants > 7:
                           print("High consonants(>7) count is an indicator of DGA domain\n" "This domain scored: %d" % domain_consonants)
                    if domain_length > 12:
                           print("Long domain name(>12) can also indicate DGA\n" "This domain scored: %d" % domain_length)
                    #model_data = pickle.load(open('gib_model.pki', 'rb'))
                    #l = input()
                    #model_mat = model_data['mat']
                    #print(model_mat)
                    #print(domain_without_sub)
                    global l
                    l = domain_without_sub
                    global log_prob_mat
                    log_prob_mat = model_mat
                    threshold = model_data['thresh']
                    if not dga_inspector().avg_transition_prob() > threshold:
                           print("Domain %s is DGA!" % args.domain)
                    else: 
                           print("Domain %s is clean!" % args.domain)

    def avg_transition_prob(self):
              print(l)
              """ Return the average transition prob from l through log_prob_mat. """
              log_prob = 0.0
              transition_ct = 0
              global n
              n = 2
              global accepted_chars 
              accepted_chars = 'abcdefghijklmnopqrstuvwxyz '
              global pos
              pos = dict([(char, idx) for idx, char in enumerate(accepted_chars)]) 
              #print("pos", pos)
              s = domain_without_sub
              i = 0
              for i in range(0, len(s), 1):
                 
                  try :
                     a, b = s[i:i+2]
                     #print("s[i:i+2]", s[i:i+2])
                     #print("a, b", a, b)
                     #print("[pos[a]][pos[b]]",[pos[a]]+[pos[b]])
                     log_prob += log_prob_mat[pos[a]][pos[b]]
                     transition_ct += 1
                     #print("transition_ct", transition_ct)
                     #print("log_prob", log_prob)
                    
                  except Exception:
                                  pass


              #print("transition_ct_final", transition_ct)
              #print("log_prob_final", log_prob)
              # The exponentiation translates from log probs to probs.
              #print("math.exp(log_prob / (transition_ct or 1)", math.exp(log_prob / (transition_ct or 1)))
              return math.exp(log_prob / (transition_ct or 1))

    




my_parser = argparse.ArgumentParser()
my_parser.add_argument("-d", "--domain", help="Domain to check")
my_parser.add_argument("-f", "--file", help="File with domains. One per line")
args = my_parser.parse_args()
model_data = pickle.load(open('gib_model.pki', 'rb'))
model_mat = model_data['mat']
       
def main():

            
            if args.domain :
                    dga_inspector(domain = args.domain).domain_check()
                    print("Analysing domain...")
                    dga_inspector().entropy_check()

            elif args.file:
                    domains = dga_inspector(filename = args.file).read_file()
                    results = {"domain": "", "is_dga": "", "high_consonants": "", "high_entropy": "", "long_domain": ""}
                    with open("dga_domains.json", "w") as f:
                        for domain in domains:
                            print("Working on %s" % domain)
                            results["domain"] = domain
                            if dga_inspector(domain).domain_check():
                                domain_without_sub, domain_entropy, domain_consonants, domain_length = dga_inspector(domain).domain_check()
                                if domain_entropy > 3.8:
                                    results["high_entropy"] = domain_entropy
                                elif domain_consonants > 7:
                                    results["high_consonants"] = domain_consonants
                                elif domain_length > 12:
                                    results["long_domain"] = domain_length
                                global l
                                l = domain_without_sub
                                global log_prob_mat
                                log_prob_mat = model_mat
                                threshold = model_data['thresh']

                                if not dga_inspector().avg_transition_prob() > threshold and domain_length <= 6:
                                    results["is_dga"] = True
                                else:
                                    results["is_dga"] = False
                            json.dump(results, f, indent=4)
                    print("File dga_domains.json is created")

main()
