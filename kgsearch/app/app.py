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

__all__ = ["Search", "create_app", "save_metadata"]


def save_metadata(origin, source):
    """Export metadata to the library."""
    with open(origin, "r") as f:
        metadata = json.load(f)

    with open(source, "w") as f:
        json.dump(metadata, f, indent=4)


class Search:
    """Search over KG."""

    def __init__(self, file: str) -> None:

        self.colors = ["#00A36C", "#9370DB", "#bbae98", "#7393B3", "#677179", "#318ce7", "#088F8F"]
        self.metadata = {}

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
                tfidf=TfidfVectorizer(lowercase=True, ngram_range=(3, 7), analyzer="char"),
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

    def save(self, path):
        """Save the search object."""
        with open(path, "wb") as f:
            pickle.dump(self, f)
        return self

    def load_metadata(self, path):
        """Load metadata"""
        with open(path, "r") as f:
            self.metadata = json.load(f)
        return self

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

    def __call__(self, query: str, k: int, n: int, p: int):
        nodes, links = [], []
        entities, h_r_t = {}, {}
        prune = collections.defaultdict(int)

        candidates, seen = [], {}
        for q in query.split(";"):
            answer = self.retriever(q.strip())[: int(k)]
            for candidate in answer:
                if candidate["label"] not in seen:
                    candidates.append(candidate)
                    seen[candidate["label"]] = True

        for group, e in enumerate(candidates):

            e = e["label"]

            nodes.append(
                {
                    "id": e,
                    "group": group,
                    "color": "#960018",
                    "fontWeight": "bold",
                    "metadata": self.metadata.get(e, {}),
                }
            )

            entities[e] = True

        for group, e in enumerate(candidates):

            e = e["label"]
            color = self.colors[group % len(self.colors)]
            match = self.explore(
                entities=tuple([]), neighbours=self.triples[e], entity=e, depth=0, max_depth=n
            )

            for h, t in list(match):

                if h not in entities:
                    nodes.append(
                        {
                            "id": h,
                            "group": group,
                            "color": color,
                            "metadata": self.metadata.get(h, {}),
                        }
                    )
                    entities[h] = True

                if t not in entities:
                    nodes.append(
                        {
                            "id": t,
                            "group": group,
                            "color": color,
                            "metadata": self.metadata.get(t, {}),
                        }
                    )
                    entities[t] = True

                for r in self.relations[f"{h}_{t}"]:
                    if f"{h}_{r}_{t}" not in h_r_t:
                        links.append({"source": h, "target": t, "value": 1, "relation": r})
                        h_r_t[f"{h}_{r}_{t}"] = True
                        prune[h] += 1
                        prune[t] += 1

                for r in self.relations[f"{t}_{h}"]:
                    if f"{t}_{r}_{h}" not in h_r_t:
                        links.append({"source": t, "relation": r, "target": h, "value": 1})
                        h_r_t[f"{t}_{r}_{h}"] = True
                        prune[h] += 1
                        prune[t] += 1
        # Prune
        if p > 1:
            links = [
                link for link in links if prune[link["source"]] >= p and prune[link["target"]] >= p
            ]

            nodes = [node for node in nodes if prune[node["id"]] >= p]

        return {"nodes": nodes, "links": links}


def create_app():
    app = Flask(__name__)
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
    app.config["CORS_HEADERS"] = "Content-Type"
    CORS(app, resources={r"/search/*": {"origins": "*"}})

    @app.route("/search/<k>/<n>/<p>/<query>", methods=["GET"])
    @cross_origin()
    def get(k: int, n: int, p: int, query: str):

        path = pathlib.Path(__file__).parent.joinpath("./../data")

        if os.path.exists(os.path.join(path, "search.pkl")):
            with open(os.path.join(path, "search.pkl"), "rb") as f:
                search = pickle.load(f)
        else:
            search = Search(file=os.path.join(path, "data.csv")).save(
                os.path.join(path, "search.pkl")
            )

        if os.path.exists(os.path.join(path, "metadata.json")):
            search = search.load_metadata(path=os.path.join(path, "metadata.json"))

        return json.dumps(search(query=query, k=int(k), n=int(n), p=int(p)))

    return app
