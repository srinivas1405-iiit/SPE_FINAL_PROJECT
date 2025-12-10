import json
import time
import sys
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import csv
import tensorflow as tf
import tensorflow_hub as hub
from flask import Flask, render_template, jsonify



def connect2ES():
    # connect to ES on localhost on port 9200
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if es.ping():
            print('Connected to ES!')
    else:
            print('Could not connect!')
            sys.exit()

    print("*********************************************************************************");
    return es

def keywordSearch(es, q):
    #Search by Keywords
    b={
            'query':{
                'match':{
                    "title":q
                }
            }
        }

    res= es.search(index='questions-index',body=b)

    return res


# Search by Vec Similarity
def sentenceSimilaritybyNN(es, sent):
    query_vector = tf.make_ndarray(tf.make_tensor_proto(embed([sent]))).tolist()[0]
    b = {"query" : {
                "script_score" : {
                    "query" : {
                        "match_all": {}
                    },
                    "script" : {
                        "source": "cosineSimilarity(params.query_vector, 'title_vector') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
             }
        }


    #print(json.dumps(b,indent=4))
    res= es.search(index='questions-index',body=b)
    
    return res;


app = Flask(__name__)
es = connect2ES();
print("Loading/Downloading Universal Sentence Encoder (this may take a while)...")
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")


# Validating files existence
import os
base_path = os.path.dirname(os.path.abspath(__file__))
q_path = os.path.join(base_path, 'data/Questions.csv')
a_path = os.path.join(base_path, 'data/Answers.csv')

# Load Data into Memory
questions_db = {}
answers_db = {}

def load_data():
    print("Loading Questions and Answers into memory...")
    try:
        with open(q_path, encoding='latin1') as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions_db[row['Id']] = row
        
        with open(a_path, encoding='latin1') as f:
            reader = csv.DictReader(f)
            for row in reader:
                qid = row['ParentId'] # In answers, ParentId links to Question Id
                if qid not in answers_db:
                    answers_db[qid] = []
                answers_db[qid].append(row)
        print(f"Loaded {len(questions_db)} questions and {len(answers_db)} answer groups.")
    except Exception as e:
        print(f"Error loading data: {e}")

load_data()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/search/<query>')
def search_api(query):
    q = query.replace("+", " ")
    res_kw = keywordSearch(es, q)
    res_semantic = sentenceSimilaritybyNN( es, q)

    results = []
    
    # Helper to check uniqueness
    seen_ids = set()

    # Process Keyword Results
    for hit in res_kw['hits']['hits']:
        doc_id = hit['_id']
        if doc_id not in seen_ids:
            results.append({
                "id": doc_id,
                "type": "Keyword",
                "score": hit['_score'],
                "title": hit['_source']['title']
            })
            seen_ids.add(doc_id)

    # Process Semantic Results
    for hit in res_semantic['hits']['hits']:
        doc_id = hit['_id']
        if doc_id not in seen_ids:
            results.append({
                "id": doc_id,
                "type": "Semantic",
                "score": hit['_score'],
                "title": hit['_source']['title']
            })
            seen_ids.add(doc_id)
        
    return jsonify(results)

@app.route('/api/details/<q_id>')
def get_details(q_id):
    question = questions_db.get(q_id)
    answers = answers_db.get(q_id, [])
    
    if not question:
        return jsonify({"error": "Question not found"}), 404
        
    return jsonify({
        "question": question,
        "answers": answers
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
