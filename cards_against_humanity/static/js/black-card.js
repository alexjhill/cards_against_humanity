class BlackCard extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            id: "",
            text: ""
        };
    }

    // function which is called when component is added
    componentDidMount() {
        if (this.props.gameState === 0 && this.props.playerState === 2) {
            this.newCard()
        } else {
            this.getCard()
        }
    }

    componentDidUpdate(prevProps) {
        if (this.props.gameState !== prevProps.gameState && this.props.playerState !== 2) {
            this.getCard();
        }
    }


    newCard() {
        // Make a request for random black card
        axios.get('/api/' + getCookie("game_id") + '/new_black_card')
        .then(response => {
            // handle success
            this.setState({
                id: response.data.id,
                text: response.data.text
            })
        })
        .catch(error => {
            // handle error
            console.log(error);
            gameState = -1;
        });
    }

    // set black card
    pickCard(id, e) {
        this.props.updateGame(1, this.props.playerState)
        axios.post('/api/' + getCookie("game_id") + '/pick_black_card', {
            card_id: id
        })
        .catch(error => {
            // handle error
            console.log(error);
        });
    }

    getCard() {
        // Make a request for random black card
        axios.get('/api/' + getCookie("game_id") + '/get_black_card')
        .then(response => {
            // handle success
            this.setState({
                id: response.data.id,
                text: response.data.text
            })
        })
        .catch(error => {
            // handle error
            console.log(error);
            gameState = -1;
        });
    }

    render() {
        if (this.props.gameState === 0) { // black card selection
            if (this.props.playerState === 0) {
                return (
                    <div className="float-right">
                        <div className="">
                            <div className="card-body">
                                <h5 className="card-title text-muted">Waiting for Card Tzar to pick a black card...</h5>
                            </div>
                        </div>
                    </div>
                )
            } else if (this.props.playerState === 1) {
                return <div className="loading-sprite"><div></div><div></div><div></div><div></div></div>
            } else if (this.props.playerState === 2) {
                return (
                    <div className="black-card">
                        <div className="card">
                            <div className="card-body">
                                <p className="card-title">{ this.state.text }</p>
                            </div>
                        </div>
                        <div className="black-card-btns">
                            <button className="btn btn-secondary" onClick={(e) => this.newCard(e)}>New card</button>
                            <button className="btn btn-primary" onClick={(e) => this.pickCard(this.state.id, e)}>Pick card</button>
                        </div>
                    </div>

                )
            } else {
                return <div className="loading-sprite"><div></div><div></div><div></div><div></div></div>
            }
        } else { // card playing or winner selection
            return (
                <div className="black-card">
                    <div className="card">
                        <div className="card-body">
                            <p className="card-title">{ this.state.text }</p>
                        </div>
                    </div>
                </div>
            )
        }
    }
}
