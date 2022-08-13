<div align="center">
  <h1>KGSearch</h1>
</div>

![](kgsearch.gif)

KGSearch is a minimalist tool for searching and viewing entities in a graph and is dedicated to a local environment. The application provides a Python client with three distinct terminal commands: `add, start, open`. The application default proposes to search through the knowledge graph [Countries](https://www.aaai.org/ocs/index.php/SSS/SSS15/paper/view/10257/10026). You can explore the borders we must cross to get from one country to another and see how small the 🌍 is.

## Installation

```sh
pip install git+https://github.com/raphaelsty/kgsearch
```

## ✅ Quick Start

The `start` command starts the API and opens the user interface:

```sh
kg start
```

## ⭐️ Query

KGSearch suggests performing multiple queries via the `;` separator.

The query `france;germany;china` will be divided into three subqueries `france`, `germany`, and `china` to visualize the interactions between the entities of our choice.

The `top K` field allows selecting the number of candidate entities retrieved by the search engine (1 by default).

The `neighbours` field selects the number of neighbors to be displayed (1 by default).

The `prune` field removes entities that have fewer than `prune` connections to other entities (1 by default).

## 🤖 Custom KG

We can add our graph to KGSearch via the command:

```sh
kg add -f data.csv
```

The graph must be saved in CSV format and structured as triples (head, relation, tail) with a comma separator and without column names. Here is an example of a compatible CSV file:

```sh
senegal,neighbor,gambia
senegal,neighbor,mauritania
senegal,neighbor,mali
senegal,neighbor,guinea-bissau
senegal,neighbor,guinea
```

We can also add custom metadata for each entity to be displayed in the user interface using `meta -f`:

```sh
kg meta -f metadata.json
```

where the `metadata.json` file has the label of the entity as a key and a set of characteristics:

```json
{
  "senegal": {"url": "https://en.wikipedia.org/wiki/senegal"},
  "gambia": {"url": "https://en.wikipedia.org/wiki/gambia"},
  "mauritania": {"url": "https://en.wikipedia.org/wiki/gambia"},
  "mali": {"url": "https://en.wikipedia.org/wiki/mali"},
}
```

## 📑 Notes

If you have already started the application, you can reopen a window with the open command:

```sh
kg open
```

The library [Cherche](https://github.com/raphaelsty/cherche) provides the entity search engine. KGSearch relies on a local flask API. The user interface is developed in React and uses the [3D Force-Directed Graph](https://github.com/vasturiano/3d-force-graph) library.