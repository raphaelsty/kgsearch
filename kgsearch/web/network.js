class Search extends React.Component {
    constructor(props) {
        super(props);
        this.state = { query: '', k: 5, n: 2 };
        this.handleChangeText = this.handleChangeText.bind(this);
        this.handleChangeTopK = this.handleChangeTopK.bind(this);
        this.handleChangeNeighbours = this.handleChangeNeighbours.bind(this)
    }

    handleChangeText(event) {
        this.setState({ query: event.target.value });
        plot(event.target.value, this.state.k, this.state.n)
    }

    handleChangeTopK(event) {
        this.setState({ k: event.target.value });
        plot(this.state.query, event.target.value, this.state.n)
    }

    handleChangeNeighbours(event) {
        this.setState({ n: event.target.value });
        plot(this.state.query, this.state.k, event.target.value)
    }


    render() {
        return (
            <React.Fragment>
                <input id="search" type="text" placeholder="Query" value={this.state.text} onChange={this.handleChangeText} />
                <label for="topk" class="label">Top K</label>
                <input id="topk" type="number" value={this.state.k} onChange={this.handleChangeTopK} />
                <label for="topk" class="label">Neighbours</label>
                <input id="n" type="number" value={this.state.n} onChange={this.handleChangeNeighbours} />
            </React.Fragment>
        );
    }
}


const plot = function (query, k, n) {
    fetch("http://127.0.0.1:5000/search/" + k.toString() + "/" + n.toString() + "/" + query).then(res => res.json()).then(data => {
        ReactDOM.render(
            <ForceGraph3D
                graphData={data}
                nodeAutoColorBy="group"
                nodeThreeObject={node => {
                    const sprite = new SpriteText(node.id);
                    sprite.color = node.color;
                    sprite.textHeight = 8;
                    return sprite;
                }}
            />,
            document.getElementById('graph')
        );
    });
}

const root = ReactDOM.createRoot(document.getElementById('backsearch'));
root.render(<Search />);

