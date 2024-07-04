from sentence_transformers import SentenceTransformer
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import openai
# from mistralai.client import MistralClient, ChatMessage
import json
from decouple import config
from datetime import datetime, timedelta
import numpy as np

# MISTRAL_API_KEY = config("MISTRAL_API_KEY")
OPENAI_API_KEY = config("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)
# mistral_client = MistralClient(api_key=MISTRAL_API_KEY)


# Get completion
def get_completion(messages, model="gpt-3.5-turbo-1106", max_tokens=500, temperature=0, ai="chatgpt", format=None):
    if ai == "chatgpt":
        if format == None:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                response_format=format,
                max_tokens=max_tokens,
            )

    # elif ai == "mistral":

    #     messages = [ChatMessage(
    #         role=message["role"], content=message["content"]) for message in messages]
    #     response = mistral_client.chat(
    #         messages=messages,
    #         model="mistral-small",
    #         temperature=temperature,
    #     )
    assistant_reply = response.choices[0].message.content
    return assistant_reply


# Get similarity between two sentences
"""def get_similarity(txt1_embeddings, txt2_embeddings):
    dot_product = np.dot(np.array(txt1_embeddings), np.array(txt2_embeddings).T)
    norm_txt1_embeddings = np.linalg.norm(txt1_embeddings)
    norm_txt2_embeddings = np.linalg.norm(txt2_embeddings)

    similarity = dot_product / (norm_txt1_embeddings * norm_txt2_embeddings)
    return similarity"""


def get_similarity(txt1_embeddings, txt2_embeddings):
    return cosine_similarity(txt1_embeddings, txt2_embeddings)


# Get the embedding of a sentence
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(txt1):
    '''
    INTPUT: txt1: string
    OUTPUT: txt1_embeddings: numpy array
    '''
    txt1_embeddings = model.encode(txt1)

    return txt1_embeddings


def add_episodic(agent, event, time, importance):
    '''
    INTPUT: agent, event
    OUTPUT: None
    '''
    file_dir = f"back_end/memory/{agent.name}/episodic.json"
    embeddings = get_embedding(event)

    with open(file_dir, 'r') as json_file:
        data = json.load(json_file)

    data["embeddings"][event] = embeddings.tolist()
    data["node"].append([time, event, importance])

    with open(file_dir, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def retrieve_episodic(agent, context, n=5):
    '''
    INTPUT: agent, context
    OUTPUT: list of n events
    '''
    file_dir = f"back_end/memory/{agent.name}/episodic.json"
    with open(file_dir, 'r') as json_file:
        data = json.load(json_file)
    embeddings = data["embeddings"]
    node = np.array(data["node"])
    context_embeddings = get_embedding([context])
    if node.size == 0:
        return [("", "")]

    similarity = cosine_similarity(
        list(embeddings.values()), context_embeddings)

    index = np.argsort(similarity, axis=0)[-n:]

    # Adjust n to the actual number of elements that can be retrieved
    n = min(len(index), n)

    results = [(node[i][1], node[i][2]) for i in range(n)]

    return results


def visualize_embeddings(file_path, threshold=0.75):
    """
    Creates and displays a graph visualizing the cosine similarity between multiple event embeddings.
    """

    try:
        with open(file_path + 'episodic.json', 'r') as json_file:
            data = json.load(json_file)
            embeddings = data["embeddings"]
    except FileNotFoundError:
        print(f"file {file_path} cannot be found")
        return
    # Create an empty graph
    G = nx.Graph()

    # Add nodes for each event
    for event in embeddings.keys():
        G.add_node(event)

    # Calculate cosine similarity between each pair of embeddings and add an edge if the similarity is high enough
    event_names = list(embeddings.keys())
    for i in range(len(event_names)):
        for j in range(i + 1, len(event_names)):
            event_i = event_names[i]
            event_j = event_names[j]
            similarity = cosine_similarity([embeddings[event_i]], [
                                           embeddings[event_j]])[0][0]

            if similarity > threshold:
                G.add_edge(event_i, event_j, weight=round(similarity, 2))

    pos = nx.spring_layout(G)

    plt.figure(figsize=(15, 10))

    # Dessinez seulement les nÅuds
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=2500)

    # Filtrer et dessiner uniquement les arÃªtes qui respectent le seuil
    edges_to_draw = [(u, v) for u, v, d in G.edges(
        data=True) if d['weight'] > threshold]
    weights = [G[u][v]['weight'] * 10 for u, v in edges_to_draw]
    nx.draw_networkx_edges(G, pos, edgelist=edges_to_draw,
                           width=weights, edge_color=weights, edge_cmap=plt.cm.Blues)

    # Dessiner les labels sÃ©parÃ©ment
    nx.draw_networkx_labels(G, pos, font_size=9)

    edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(
        data=True) if d['weight'] > threshold}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title('Cosine Similarity Network of Events')
    plt.axis('off')  # Cache les axes pour une meilleure visibilitÃ©
    plt.show()


# Get the duration of a task in minutes
def get_duration(start, end):
    '''
    INPUT:
        start: 'hh:mm AM/PM'
        end: 'hh:mm AM/PM'
    OUTPUT:
        minutes: int
    '''
    if len(start) == 7:
        start = "0" + start
    if len(end) == 7:
        end = "0" + end

    if start[6:] == end[6:]:
        minutes = int(end[:2])*60 + int(end[3:5]) - \
            int(start[:2])*60 - int(start[3:5])
        return minutes
    elif start[6:] == "AM" and end[6:] == "PM":
        minutes = (12 - int(start[:2]))*60 - \
            int(start[3:5]) + int(end[:2])*60 + int(end[3:5])
        return minutes

# Get the time in the format 'hh:mm AM/PM' after adding minutes to a time in the same format


def add_minutes_to_time(time_str, minutes):
    '''
    INTPUT:
        time_str: 'hh:mm AM/PM'
        minutes: int
    OUTPUT:
        result_time_str: 'hh:mm AM/PM'
    '''
    # Parse the INTPUT time string
    time_format = '%I:%M %p'
    base_time = datetime.strptime(time_str, time_format)

    # Calculate the new time by adding the duration
    new_time = base_time + timedelta(minutes=minutes)

    # Format the result as 'hh:mm AM/PM'
    result_time_str = new_time.strftime(time_format)

    return result_time_str
