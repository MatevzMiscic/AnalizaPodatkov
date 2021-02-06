import re
import os
import orodja

LAST_CONTEST = 1437
NUMBER = 200
DATA_DIR = "podatki"
PROCESSED_DIR = "obdelani_podatki"

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
    r'(?:title="(?P<proglang>.*?)".*?>.*?)?'
    #r'<span class="(?P<type>.*?)">(?P<submissions>.*?)</span>.*?'
    r'<span class=".*?">.*?</span>.*?'
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
            os.path.join(DATA_DIR, f"contest-{i + 1}.html"), 
            False
        )

def valid_contests():
    '''Nekatera tekmovanja so ekipna in nekatera niso odprta za vse tekmovalce. Takih tekmovanj ne bomo analizirali. 
    Ta funkcija shrani števila vseh tekmovanj, ki imajo vsaj 200 udeležencev in so individualna.'''
    ranks = {"Legendary Grandmaster": 11, "International Grandmaster": 10, "Grandmaster": 9, "International Master": 8, "Master": 7,
     "Candidate Master": 6, "Expert": 5, "Specialist": 4, "Apprentice": 3, "Pupil": 2, "Newbie": 1, "Unrated,": 0, "Unrated": 0}
    valid = []
    for i in range(NUMBER):
        string = orodja.vsebina_datoteke(os.path.join(DATA_DIR, f"contest-{i + 1}.html"))
        participants = 0
        found = 0
        tmin = 100
        tmax = 0
        example = None
        ranks_correct = True
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
                # validate rank
                rank_and_name = contestant["rank"].split(" ")
                rank = " ".join(rank_and_name[:-1])
                if rank not in ranks:
                    ranks_correct = False
                    example = contestant.groupdict()["rank"]
        OK = (found == 200) and (tmin == tmax) and ranks_correct
        if OK:
            valid.append(str(i + 1))
        else:
            print(f"Contest {num_to_contest(i + 1)} ({i + 1}) ... ", end="")
            if found < 200:
                print(f"not enough participants: {found} / {participants}")
            elif tmin < tmax:
                print(f"missing tasks: {tmin} / {tmax}")
            elif not ranks_correct:
                print("invalid rank:", example)        
    orodja.zapisi_v_datoteko(
        " ".join(valid), 
        os.path.join(DATA_DIR, "valid_contests.txt"), 
    )
    print(len(valid))

def extract_tasks(string):
    tasks = []
    for i, match in enumerate(re.finditer(task_pat, string), 1):
        task = match.groupdict()
        # poiščemo pragramski jezik
        if "proglang" not in task:
            task["proglang"] = None
        elif task["proglang"] is not None:
            low = task["proglang"].lower()
            table = ["++", "java ", "py"]
            langs = ["c++", "java", "python"]
            for root, lang in zip(table, langs):
                if root in low:
                    task["proglang"] = lang
                    break
        # kolikokrat je tekmovalec oddal domnevno rešitev (tega podatka ne potrebujemo)
        """
        if "submissions" not in task or task["submissions"] is None:
            task["submissions"] = 0
        else:
            if task["submissions"] == "+":
                task["submissions"] = 1
            elif "&nbsp;" in task["submissions"]:
                task["submissions"] = 0
            else:
                try:
                    task["submissions"] = int(task["submissions"])
                    if task["submissions"] > 0:
                        task["submissions"] += 1
                except ValueError:
                    task["submissions"] = None
        """
        # čas reševanja
        if "time" not in task:
            task["time"] = None
        elif task["time"] is not None:
            hour_min = task["time"].split(":")
            task["time"] = 60 * int(hour_min[0]) + int(hour_min[1])
        # zaporedna šetvilka naloge na tekmovanju
        task["number"] = i
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
    if contestant["rank"] == "Unrated,":
        contestant["rank"] = "Unrated"
    if "country" not in contestant:
        contestant["country"] = None
    if contestant["country"] == "Япония":
        contestant["country"] = "Japan"
    contestant["tasks"] = extract_tasks(contestant["tasks"])
    return contestant

def get_userdict():
    print("in")
    nums = orodja.vsebina_datoteke(os.path.join(DATA_DIR, "valid_contests.txt")).split(" ")
    valid = [int(num) for num in nums]
    users = {}
    for i in valid:
        print(i)
        string = orodja.vsebina_datoteke(os.path.join(DATA_DIR, f"contest-{i}.html"))
        for block in re.finditer(block_pat, string):
            contestant = extract_contestant(block.group(0))
            contestant["contest"] = i
            name = contestant["name"]
            if name not in users:
                users[name] = []
            users[name].append(contestant)
    print("out")
    return users

def process_data():
    ranks = {"Legendary Grandmaster": 11, "International Grandmaster": 10, "Grandmaster": 9, "International Master": 8, "Master": 7, 
        "Candidate Master": 6, "Expert": 5, "Specialist": 4, "Apprentice": 3, "Pupil": 2, "Newbie": 1, "Unrated,": 0, "Unrated": 0}
    userdict = get_userdict()
    taskid, userid, subid, contid = 1, 1, 1, 1
    seentasks = {}
    users, tasks, submissions, contestants = [], [], [], []
    for name, user in userdict.items():
        rank = "Unrated"
        for contestant in user:
            if ranks[rank] < ranks[contestant["rank"]]:
                rank = contestant["rank"]
            for sub in contestant["tasks"]:
                if (contestant["contest"], sub["number"]) not in seentasks:
                    seentasks[(contestant["contest"], sub["number"])] = taskid
                    tasks.append({"id": taskid, "contest": contestant["contest"], "number": sub["number"]})
                    taskid += 1
                sub["id"] = subid
                subid += 1
                sub["contestant"] = contid
                sub["task"] = seentasks[(contestant["contest"], sub["number"])]
                del sub["number"]
                submissions.append(sub)
            newcontestant = {"id": contid, "user": userid, "contest": contestant["contest"], "place": contestant["place"]}
            contestants.append(newcontestant)
            contid += 1
        newuser = {"id": userid, "name": name, "rank": rank, "country": user[0]["country"]}
        users.append(newuser)
        userid += 1
    orodja.zapisi_csv(users, ["id", "name", "rank", "country"], os.path.join(PROCESSED_DIR, "users.csv"))
    orodja.zapisi_csv(tasks, ["id", "contest", "number"], os.path.join(PROCESSED_DIR, "tasks.csv"))
    orodja.zapisi_csv(submissions, ["id", "contestant", "task", "proglang", "time"], os.path.join(PROCESSED_DIR, "submissions.csv"))
    orodja.zapisi_csv(contestants, ["id", "user", "contest", "place"], os.path.join(PROCESSED_DIR, "contestants.csv"))
    print("done")

process_data()