# gellany_dga

we forked from https://github.com/exp0se/dga_detector and destructions code and restruction it as Object-oriented programming (OOP) skeleton to product new class and reduce fale postive and increase probelm solving solution with replece deeply hardcore in lines.
DGA domain detection is based on ngram analysis with trained markov chain model. we replace ngram with simple algo

entropy - High entropy is another indicator of DGA domain. Threshold is 3.8
consonants - High consonants count is an indicator of DGA domain. Threshold is 7
ength - High domain length can also indicate DGA. Threshold is 12.



<code>python3 gellany_dga.py --file test.txt
Working on isqekc.com
isqekc
Working on test.com
Working on google.com
google
Working on 4learnz.com
4learnz
Working on yahoo.com
File dga_domains.json is created</code><br>
<code>python3 gellany_dga.py --domain google.com
Analysing domain...
google
Domain google.com is clean!</code><br>
<code>python3 gellany_dga.py --domain isqekc.com
Analysing domain...
isqekc
Domain isqekc.com is DGA!
</code><br>

<code>python3 gellany_dga.py -h
usage: gellany_dga.py [-h] [-d DOMAIN] [-f FILE]

optional arguments:
  -h, --help            show this help message and exit
  -d DOMAIN, --domain DOMAIN
                        Domain to check
  -f FILE, --file FILE  File with domains. One per line</code><br>

next steps :
   we will integration with alienvalut api , keep watch
 https://otx.alienvault.com/browse/global/indicators?q=dga&include_inactive=0&sort=-modified&page=1&indicatorsSearch=dga  
  
