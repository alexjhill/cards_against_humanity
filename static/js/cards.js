class HandCards extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            cards: []
        };
    }

    // function which is called when component is added
    componentDidMount() {
        // get cards
        this.fetchCards();
    }

    fetchCards() {
        this.setState({cards: this.state.cards});
        // Make a request for cards for player
        axios.get('/game/get_cards')
            .then(response => {
                // handle success
                this.setState({cards: response.data})
            })
            .catch(error => {
                // handle error
                console.log(error);
                this.setState({cards: this.state.players})
            });
    }

    playCard() {
        alert("test");
    }

    render() {
        return this.state.cards.map((card) =>
                <li key={ card._id.$oid }>
                    <div className="card hand-card" onClick={(e) => this.playCard(id, e)}>
                        <div className="card-body">
                            <h5 className="card-title">{ card.text }</h5>
                        </div>
                    </div>
                </li>);
    }
}

ReactDOM.render(
    <HandCards />,
    document.getElementById('hand-cards')
);
