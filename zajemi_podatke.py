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
    r'(?:<img class="standings-flag".*?alt=".*?".*?title="(?P<country>.*?)"/>.*?)?'
    r'<a href=".*?" title="(?P<rank>.*?)".*?</a>.*?</td>.*?'
    r'<td>.*?(?:.*?).*?</td>.*?' # solved tasks 
    r'(?:<td>.*?(?:.*?).*?</td>.*?)?' # penalty
    r'(?:<td style=".*?">(?:.*?)</td>.*?)?' # hacks
    r'(?P<tasks><td.*?)'
    r'</tr>',
    flags=re.DOTALL
)

task_pat = re.compile(
    r'<td.*?'
    r'(?:contestId=".*?".*?)?'
    r'(?:problemId=".*?".*?)?'
    r'(?:title="(?P<programski_jezik>.*?)".*?>.*?)?'
    r'<span class=".*?">(?P<submissions>.*?)</span>.*?'
    r'(?:<span class=".*?">(?P<time>.*?)</span>.*?)?'
    r'</td>',
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

def valid_contests():
    '''Nekatera tekmovanja so ekipna in nekatera niso odprta za vse tekmovalce. Takih tekmovanj ne bomo analizirali. 
    Ta funkcija shrani števila vseh tekmovanj, ki imajo vsaj 200 udeležencev in so individualna.'''
    valid = []
    for i in range(NUMBER):
        string = orodja.vsebina_datoteke(os.path.join(DIR, f"contest-{i + 1}.html"))
        participants = 0
        found = 0
        tmin = 100
        tmax = 0
        for block in re.finditer(block_pat, string):
            participants += 1
            contestant = re.search(contestant_pat, block.group(0))
            if contestant:
                found += 1
                t = 0
                iterator = re.finditer(task_pat, contestant.groupdict()["tasks"])
                for task in iterator:
                    t += 1
                tmin = min(tmin, t)
                tmax = max(tmax, t)
        OK = (found == 200) and (tmin == tmax)
        if OK:
            valid.append(str(i + 1))
        else:
            print(f"Contest {num_to_contest(i + 1)} ({i + 1}) ... ", end="")
            if found < 200:
                print(f"not enough participants: {found} / {participants}")
            elif tmin < tmax:
                print(f"missing tasks: {tmin} / {tmax}")
    orodja.zapisi_v_datoteko(
        " ".join(valid), 
        os.path.join(DIR, "valid_contests.txt"), 
    )
    print(len(valid))

def extract_tasks(string):
    tasks = []
    for match in re.finditer(task_pat, string):
        task = match.groupdict()
        # poiščemo pragramski jezik
        if "programski_jezik" not in task:
            task["programski_jezik"] = None
        elif task["programski_jezik"] is not None:
            low = task["programski_jezik"].lower()
            table = ["++", "java ", "py"]
            langs = ["c++", "java", "python"]
            for root, lang in zip(table, langs):
                if root in low:
                    task["programski_jezik"] = lang
                    break
        # kolikokrat je tekmovalec oddal domnevno rešitev
        if "submissions" not in task or task["submissions"] is None:
            task["submissions"] = 0
        else:
            if task["submissions"] == "+":
                task["submissions"] = 1
            elif task["submissions"] == "&nbsp;":
                task["submissions"] = 0
            else:
                task["submissions"] = int(task["submissions"])
                if task["submissions"] > 0:
                    task["submissions"] += 1
        # čas reševanja
        if "time" not in task:
            task["time"] = None
        elif task["time"] is not None:
            hour_min = task["time"].split(":")
            task["time"] = 60 * int(hour_min[0]) + int(hour_min[1])
        tasks.append(task)
    return tasks

def extract_contestant(string):
    match = re.search(contestant_pat, string)
    if match is None:
        return None
    contestant = match.groupdict()
    contestant["id"] = int(contestant["id"])
    contestant["place"] = int(contestant["place"])
    rank_and_name = contestant["rank"].split(" ")
    contestant["name"] = rank_and_name[-1]
    contestant["rank"] = " ".join(rank_and_name[:-1])
    if "country" not in contestant:
        contestant["country"] = None
    contestant["tasks"] = extract_tasks(contestant["tasks"])
    return contestant

def real():
    nums = orodja.vsebina_datoteke(os.path.join(DIR, "valid_contests.txt")).split(" ")
    valid = [int(num) for num in nums]
    # debug
    valid = [200]
    users = {}
    for i in valid:
        string = orodja.vsebina_datoteke(os.path.join(DIR, f"contest-{i}.html"))
        for block in re.finditer(block_pat, string):
            contestant = extract_contestant(block.group(0))
            name = contestant["name"]
            if name not in users:
                users[name] = []
            users[name].append(contestant)
    return users
    

def analyse():
    for i in range(NUMBER):
        string = orodja.vsebina_datoteke(os.path.join(DIR, f"contest-{i + 1}.html"))
        n = 0
        m = 0
        tmin = 100
        tmax = 0
        for block in re.finditer(block_pat, string):
            n += 1
            contestant = re.search(contestant_pat, block.group(0))
            if contestant is not None:
                m += 1
                t = 0
                iterator = re.finditer(task_pat, contestant.groupdict()["tasks"])
                for task in iterator:
                    t += 1
                tmin = min(tmin, t)
                tmax = max(tmax, t)
        warn = ["", "           <---"]
        print(f"contest {i + 1}: contestants = {m} / {n}, tasks = [{tmin}, {tmax}]", warn[int(tmin < tmax or m < 200)])

def analyselast(num=NUMBER):
    string = orodja.vsebina_datoteke(os.path.join(DIR, f"contest-{num}.html"))
    n = 0
    m = 0
    tmin = 100
    tmax = 0
    for block in re.finditer(block_pat, string):
        n += 1
        
        #print(block.group(0))
        if n == 1: print(extract_contestant(block.group(0)))
        #break

        contestant = re.search(contestant_pat, block.group(0))
        if contestant is not None:
            #print("bruh")
            m += 1
            t = 0
            iterator = re.finditer(task_pat, contestant.groupdict()["tasks"])
            for task in iterator:
                t += 1
            tmin = min(tmin, t)
            tmax = max(tmax, t)
            #print(contestant.groupdict()["place"], ": ", t)
        #break
    print(f"contestants = {m} / {n}, tasks = [{tmin}, {tmax}]")

#analyse()
#analyselast()
print(real())