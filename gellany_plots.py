import pickle
import tldextract
import argparse
import json
import math
import re

class dga_inspector():
    
# init method or constructor
    def __init__(self, var1= None, title1 = '', var2 = None, title2 = '', transformed = False, read_file = None, hue= None, type =None, label = None, drop = None, encode = None):

                          self.data = data
                          self.var1 = var1
                          self.title1 = title1
                          self.var2 = var2
                          self.title2 = title2
                          self.transformed = transformed
                          self.read_file = str(read_file)
                          self.hue = hue
                          self.type = type
                          self.df_test = df_test
                          self.label = label
                          self.drop = drop
                          self.encode = encode
          
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


    def main():
        parser = argparse.ArgumentParser(description="DGA domain detection")
        parser.add_argument("-d", "--domain", help="Domain to check")
        parser.add_argument("-f", "--file", help="File with domains. One per line")
        args = parser.parse_args()
        model_data = pickle.load(open('gib/gib_model.pki', 'rb'))
        model_mat = model_data['mat']
        threshold = model_data['thresh']
        if args.domain:
            if domain_check(args.domain):
                domain_without_sub, domain_entropy, domain_consonants, domain_length = domain_check(args.domain)
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

      
                  
          
