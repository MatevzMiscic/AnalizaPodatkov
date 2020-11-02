import re
import os
import orodja

LAST_CONTEST = 1437
NUMBER = 200
DIR = "podatki"

block_pat = re.compile(
    r'<tr participantId="\d+">'
    r'.*?'
    r'</tr>',
    flags=re.DOTALL
)

contestant_pat = re.compile(
    r'<tr participantId="(?P<id>\d+?)">.*?'
    r'<td>\s*?(?P<place>\d+)\s*?</td>.*?'
    r'<td class="contestant-cell".*?>.*?'
    r'<a href=".*?" title="(?P<rank>.*?)".*?</a>.*?</td>.*?'
    r'<td>.*?(?P<solved_tasks>.*?).*?</td>.*?'
    r'<td>.*?(?P<penalty>.*?).*?</td>.*?'
    r'<td style=".*?">(?P<hacks>.*?)</td>.*?'
    r'(?P<tasks><td.*?)'
    r'</tr>',
    flags=re.DOTALL
)

task_pat = re.compile(
    r'<tr participantId="\d+">'
    r'.*?'
    r'</tr>',
    flags=re.DOTALL
)

def num_to_contest(num):
    return LAST_CONTEST - NUMBER + num

def contest_to_num(contest):
    return contest - LAST_CONTEST + NUMBER

def load():
    prvi = LAST_CONTEST - NUMBER + 1
    for i in range(NUMBER):
        orodja.shrani_spletno_stran(
            f"https://codeforces.com/contest/{prvi + i}/standings", 
            os.path.join(DIR, f"contest-{i + 1}.html"), 
            False
        )

def analyse():
    for i in range(NUMBER):
        string = orodja.vsebina_datoteke(os.path.join(DIR, f"contest-{i + 1}.html"))
        n = 0
        m = 0
        for block in re.finditer(block_pat, string):
            #if n == 0: print(block.group(0))
            n += 1
            if re.search(contestant_pat, block.group(0)) is not None: m += 1
        print(f"contest {i + 1}:" , n, m)

def analyselast(num=NUMBER):
    string = orodja.vsebina_datoteke(os.path.join(DIR, f"contest-{num}.html"))
    n = 0
    m = 0
    for block in re.finditer(block_pat, string):
        #if n == 0: print(block.group(0))
        n += 1
        if re.search(contestant_pat, block.group(0)) is not None: m += 1
    print(f"contest {num}:" , n, m)

#load()
#analyse()
analyselast()