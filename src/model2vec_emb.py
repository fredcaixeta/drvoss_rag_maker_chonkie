# Model2Vec
from model2vec import StaticModel

def load_model2vec(embedder="minishlab/potion-base-32M"):
    model = StaticModel.from_pretrained(embedder)
    return model

def get_model2vec_embeddings(model: StaticModel, text):
    embedding = model.encode(text)
    return embedding