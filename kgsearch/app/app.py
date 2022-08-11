import collections
import json
import os
import pathlib
import pickle
from functools import lru_cache

import pandas as pd
from cherche import retrieve
from flask import Flask
from flask_cors import CORS, cross_origin
from sklearn.feature_extraction.text import TfidfVectorizer

__all__ = [
    "Search",
    "create_app",
]


class Search:
    """Search over KG."""

    def __init__(self, file: str) -> None:

        triples = pd.read_csv(file, header=None, sep=",")

        documents = [
            {"key": key, "label": label}
            for key, label in pd.concat([triples[0], triples[2]], axis="rows")
            .drop_duplicates(keep="first")
            .reset_index(drop=True)
            .to_dict()
            .items()
        ]

        self.retriever = (
            retrieve.TfIdf(
                key="key",
                on="label",
                documents=documents,
                tfidf=TfidfVectorizer(lowercase=True, ngram_range=(2, 7), analyzer="char"),
                k=30,
            )
            + documents
        )

        self.triples = collections.defaultdict(tuple)
        self.relations = collections.defaultdict(list)

        for h, r, t in triples.to_records(index=False).tolist():
            self.triples[h] += tuple([t])
            self.triples[t] += tuple([h])
            self.relations[f"{h}_{t}"].append(r)

        self.explore.cache_clear()

    @lru_cache(maxsize=10000)
    def explore(self, entities, neighbours, entity, depth, max_depth):
        depth += 1

        for neighbour in neighbours:

            entities += tuple([tuple([entity, neighbour])])

            if depth < max_depth:

                entities = self.explore(
                    entities=entities,
                    neighbours=self.triples.get(neighbour, tuple([])),
                    entity=neighbour,
                    depth=depth,
                    max_depth=max_depth,
                )

        return entities

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self, f)
        return self

    def __call__(self, query: str, k: int, n: int):

        nodes, links = [], []
        entities, h_r_t = {}, {}

        for group, e in enumerate(self.retriever(query)[: int(k)]):

            e = e["label"]

            if e not in entities:
                nodes.append({"id": e, "group": group})
                entities[e] = True

            match = self.explore(
                entities=tuple([]), neighbours=self.triples[e], entity=e, depth=0, max_depth=n
            )

            match = list(match)

            for h, t in match:

                if h not in entities:
                    nodes.append({"id": h, "group": group})
                    entities[h] = True

                if t not in entities:
                    nodes.append({"id": t, "group": group})
                    entities[t] = True

                for r in self.relations[f"{h}_{t}"]:
                    if f"{h}_{r}_{t}" not in h_r_t:
                        links.append({"source": h, "target": t, "value": 1, "relation": r})
                        h_r_t[f"{h}_{r}_{t}"] = True

                for r in self.relations[f"{t}_{h}"]:
                    if f"{t}_{r}_{h}" not in h_r_t:
                        links.append({"source": t, "relation": r, "target": h, "value": 1})
                        h_r_t[f"{t}_{r}_{h}"] = True

        return {"nodes": nodes, "links": links}


def create_app():
    app = Flask(__name__)
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
    app.config["CORS_HEADERS"] = "Content-Type"
    CORS(app)

    @app.route("/search/<k>/<n>/<query>", methods=["GET"])
    @cross_origin()
    def get(k: int, n: int, query: str):
        path = pathlib.Path(__file__).parent.joinpath("./../data")

        if os.path.exists(os.path.join(path, "search.pkl")):
            with open(os.path.join(path, "search.pkl"), "rb") as f:
                search = pickle.load(f)
        else:
            search = Search(file=os.path.join(path, "data.csv")).save(
                os.path.join(path, "search.pkl")
            )

        return json.dumps(search(query=query, k=int(k), n=int(n)))

    return app
