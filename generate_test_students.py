import random, itertools, os, shutil
from app import models, db

AGENT_NAME_SIZE = 12
NUM_AGENTS      = 200
NUM_CLIENTS     = 200

# chosen from top names in australia
first_names = [
    "Julie", "Karen", "Michelle", "Helen", "Sue",
    "Elizabeth", "Sarah", "Lisa", "Kate", "Kim",
    "Rebecca", "Jane", "Susan", "Wendy", "Amanda",
    "Anne", "Christine",  "Sharon", "Jennifer", "Fiona",
    "David", "John", "Peter", "Michael", "Paul",
    "Andrew", "Mark", "Robert", "Ian", "Chris",
    "Steven", "James", "Tony", "Greg", "Benjamin",
    "Richard", "Tim", "Jason", "Stephen", "Daniel",
]

# chosen from top names in australia
last_names = [
    "Smith", "Jones", "Williams", "Brown", "Wilson",
    "Taylor", "Anderson", "Johnson", "White", "Thompson",
    "Lee", "Martin", "Thomas", "Walker", "Kelly",
    "Young", "Harris", "King", "Ryan", "Roberts",
    "Hall", "Evans", "Davis", "Wright", "Baker",
    "Campbell", "Edwards", "Clark", "Robinson", "McDonald",
    "Hill", "Scott", "Clarke", "Mitchell", "Stewart",
    "Moore", "Turner", "Miller", "Green", "Watson",
]

agent_names = set()

def agentNameGenerator(first_name, last_name, student_number):
    fnsz = len(first_name)
    lnsz = len(last_name)
    if fnsz + lnsz > AGENT_NAME_SIZE:
        if fnsz < lnsz and fnsz <= int(AGENT_NAME_SIZE*0.7):
            lnsz = AGENT_NAME_SIZE - fnsz
        elif lnsz < fnsz and lnsz <= int(AGENT_NAME_SIZE*0.7):
            fnsz = AGENT_NAME_SIZE - lnsz
        else:
            fnsz = AGENT_NAME_SIZE//2
            lnsz = AGENT_NAME_SIZE - fnsz

    while True:
        if fnsz <= 0 and lnsz <= 0:
            return student_number

        snsz = AGENT_NAME_SIZE - fnsz - lnsz
        fnpart = first_name[:fnsz]
        lnpart = last_name[:lnsz]
        snpart = student_number[:snsz]

        parts = [fnpart, lnpart, snpart]
        names = ["".join(name) for name in itertools.permutations(parts)]
        #random.shuffle(names)
        for name in names:
            if not name in agent_names:
                agent_names.add(name)
                return name

        if fnsz == 0:
            lnsz -= 1
        elif lnsz == 0:
            fnsz -= 1
        elif random.random() < 0.5:
            fnsz -= 1
        else:
            lnsz -= 1

student_numbers = set()

def studentNumberGenerator():
    while True:
        student_number = str(random.randint(10000000, 99999999))
        if not student_number in student_numbers:
            student_numbers.add(student_number)
            return student_number

def padding(string, length):
    orig_len = len(string)
    if length < orig_len:
        return string[:length]
    diff = length - orig_len
    lpad = diff//2
    rpad = diff - lpad
    return (" "*lpad) + string + (" "*rpad)

db.drop_all()
db.create_all()

student_deets_list = []

for i in range(NUM_AGENTS):
    first_name     = random.choice(first_names)
    last_name      = random.choice(last_names)
    student_number = studentNumberGenerator()
    agent_name     = agentNameGenerator(first_name, last_name, student_number)

    student_deets = {
        "id": student_number,   "first_name": first_name,
        "last_name": last_name, "agent_name": agent_name,
    }

    student = models.Student(**student_deets)
    token = student.get_token()
    student_deets["token"] = token
    student_deets_list.append(student_deets)

db.session.commit()

line1 = " | ".join([padding("id", 8),
                    padding("token", 32),
                    padding("agent_name", AGENT_NAME_SIZE),
                    "first_name last_name"])
line2 = "-"*len(line1)
lines = [line1, line2]

for student_deets in student_deets_list:
    tags = ["id", "token", "agent_name", "first_name", "last_name"]
    parts = [student_deets[tag] for tag in tags]

    last_name  = parts.pop()
    first_name = parts.pop()
    parts.append(first_name + " " + last_name)

    lines.append(" | ".join(parts))

with open("student_deets.txt", "w") as f:
    f.write("\n".join(lines))

# generate clients
dir_path = os.getcwd()
src = os.path.join(dir_path, "clients/template")
if os.path.exists(src):
    students = random.sample(student_deets_list, NUM_CLIENTS)
    for i in range(NUM_CLIENTS):
        # create client directory for agent i
        dst = os.path.join(dir_path, "clients/agent{}".format(i))
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

        # write student info file
        student = students[i]
        st_info = [student["id"], student["token"], student["agent_name"],
                   student["first_name"], student["last_name"]]
        with open("clients/agent{}/student_info.txt".format(i), "w") as f:
            f.write(" ".join(st_info))

