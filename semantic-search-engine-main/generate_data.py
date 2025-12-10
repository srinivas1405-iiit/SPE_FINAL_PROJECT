import csv
import random

# Topics to mix and match for "fake" questions
topics = ["Python", "Java", "C++", "Elasticsearch", "Flask", "Django", "React", "Docker", "Kubernetes", "AWS"]
actions = ["How to install", "debug error in", "optimize performance of", "deploy", "configure", "best practices for", "tutorial for", "connection failed in"]
details = ["on Linux", "on Windows", "with low memory", "production environment", "for beginners", "with async support", "in 2023", "after upgrade"]

def generate_questions(num=100):
    data = []
    for i in range(num):
        topic = random.choice(topics)
        action = random.choice(actions)
        detail = random.choice(details)
        
        title = f"{action} {topic} {detail}?"
        body = f"I am trying to {action.lower()} {topic} but facing issues {detail}. Please help."
        
        # Schema: Id,OwnerUserId,CreationDate,ClosedDate,Score,Title,Body
        row = [
            i + 1000, # Id
            random.randint(1, 500), # OwnerUserId
            "2023-01-01", # CreationDate
            "NA", # ClosedDate
            random.randint(0, 100), # Score
            title,
            body
        ]
        data.append(row)
    return data

def write_csv(filename, data):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Id","OwnerUserId","CreationDate","ClosedDate","Score","Title","Body"])
        writer.writerows(data)
    print(f"Generated {len(data)} questions in {filename}")

def generate_answers(questions, num_per_q=1):
    data = []
    # questions is list of rows. row[0] is Id.
    for q_row in questions:
        q_id = q_row[0]
        for i in range(num_per_q):
            # Schema: Id,OwnerUserId,CreationDate,ParentId,Score,Body
            a_id = q_id + 100000 + i
            body = f"This is an answer to question {q_id}. You should try checking the logs."
            row = [
                a_id,
                random.randint(1, 500), # OwnerUserId
                "2023-01-02", # CreationDate
                q_id, # ParentId
                random.randint(0, 50), # Score
                body
            ]
            data.append(row)
    return data

def write_answers_csv(filename, data):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Id","OwnerUserId","CreationDate","ParentId","Score","Body"])
        writer.writerows(data)
    print(f"Generated {len(data)} answers in {filename}")

if __name__ == "__main__":
    qs = generate_questions(100)
    write_csv('./SearchEngine_QA/data/Questions.csv', qs)
    
    ans = generate_answers(qs)
    write_answers_csv('./SearchEngine_QA/data/Answers.csv', ans)
