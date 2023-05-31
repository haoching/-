import json
import csv
i=0
with open("user_data.json", "r", encoding = "utf-8") as f:
    user_data = json.load(f)
d = {}
with open("member.csv","r", encoding= "utf-8") as f:
    reader = csv.reader(f)
    next(reader) # toss headers
    for id, name in reader:
        d.setdefault(id, []).append(name)
i = 0
for group in sorted(list(user_data.values()), key = lambda data: data.get('score'), reverse = True):
  if i >= 100:
    break
  student_id = group.get("student_id")
  username = d.get(student_id)
  if username is not None:
    n = username[0]
  else:
    n = student_id+"(非社員)"
  
  i+=1
  print(str(i)+":"+n)