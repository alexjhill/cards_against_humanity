class Root extends React.Component {
    constructor(props) {
        super(props);

        // Bind the this context to the updateGame function
        this.updateGame = this.updateGame.bind(this);
        this.newRound = this.newRound.bind(this);

        this.state = {
            gameState: "",
            playerState: "",
            playedCards: [],
            winner: "",
            winningCard: ""
        };
    }

    // function which is called when component is added
    componentDidMount() {
        // get cards
        this.fetchGame();
        this.timer = setInterval(() => this.fetchGame(), 5000);
    }

    // function which is called when component about to be removed
    componentWillUnmount() {
        clearInterval(this.timer);
        this.timer = null;
    }

    // This method will be sent to the child component
    updateGame(gameState, playerState) {
        this.setState({
            gameState: gameState,
            playerState: playerState
        });
    }

    fetchGame() {
        // Make a request for cards for player
        axios.get('/api/' + getCookie("game_id") + '/get_game')
        .then(response => {
            // handle success
            this.setState({
                gameState: response.data[0].state,
                playerState: response.data[1],
                playedCards: response.data[2],
                winner: response.data[3],
                winningCard: response.data[4]
            })
        })
        .catch(error => {
            // handle error
            console.log(error);
            this.setState({
                gameState: -1
            })
        });
    }

    newRound() {
        this.updateGame(0, this.state.playerState)
        axios.post('/api/' + getCookie("game_id") + '/new_round')
        .catch(error => {
            // handle error
            console.log(error);
        });
    }

    render() {
        if (this.state.gameState === 3) {
            return (
                <React.Fragment>
                    <div className="row justify-content-md-center">
                        <div className="col col-md-6 flex-column">
                            <table className="table mt-3">
                                <thead>
                                    <tr>
                                        <th scope="col">State</th>
                                        <th scope="col">Player</th>
                                        <th scope="col">Score</th>
                                    </tr>
                                </thead>
                                <tbody id="leaderboard">
                                    <Leaderboard gameState = { this.state.gameState } />
                                </tbody>
                            </table>
                            <div className="text-center alert">
                                <h4 className="mb-3">{ this.state.winner.name } won this round!</h4>
                                <button className="btn btn-primary" onClick={this.newRound} role="button">New Round</button>
                            </div>
                        </div>
                    </div>
                    <div className="row">
                        <div id="black-card" className="col col-md-6">
                            { this.state.gameState !== "" ? <BlackCard gameState = { this.state.gameState } playerState = { this.state.playerState } updateGame = { this.updateGame }/> : null }

                            <HandCards gameState = { this.state.gameState } playerState = { this.state.playerState } winningCard = {this.state.winningCard} />
                        </div>
                    </div>
                </React.Fragment>
            )
        } else {
            return (
                <React.Fragment>
                    <div className="row justify-content-md-center">
                        <div id="black-card" className="col col-md-4">
                            { this.state.gameState !== "" ? <BlackCard gameState = { this.state.gameState } playerState = { this.state.playerState } updateGame = { this.updateGame }/> : null }
                        </div>
                        <div className="col col-md-4">
                            <table className="table">
                                <thead>
                                    <tr>
                                        <th scope="col">State</th>
                                        <th scope="col">Player</th>
                                        <th scope="col">Score</th>
                                    </tr>
                                </thead>
                                <tbody id="leaderboard">
                                    <Leaderboard gameState = { this.state.gameState } />
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div className="row">
                        <ul id="hand-cards">
                            <HandCards gameState = { this.state.gameState } playerState = { this.state.playerState } playedCards = { this.state.playedCards } updateGame = { this.updateGame }/>
                            <li className="card-spacer">.</li>
                        </ul>
                    </div>
                </React.Fragment>
            )
        }
    }
}

ReactDOM.render(
    <Root />,
    document.getElementById('root')
);
