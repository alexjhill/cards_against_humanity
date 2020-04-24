class Root extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            blackCard: "Test",
            gameState: 0,
            playedCards: [],
            playerState: 0
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

    fetchGame() {
        // Make a request for cards for player
        axios.get('/game/' + getCookie("game_id") + '/get_game')
        .then(response => {
            // handle success
            this.setState({
                blackCard: response.data[0].black_card,
                gameState: response.data[0].state,
                playedCards: response.data[0].played_cards,
                playerState: response.data[1]
            })
        })
        .catch(error => {
            // handle error
            console.log(error);
            gameState = -1;
        });
    }

    render() {
        return (
            <React.Fragment>
                <div className="row justify-content-md-center my-3">
                    <div id="black-card" className="col col-md-4">
                        <BlackCard text = { this.state.blackCard } gameState = { this.state.gameState } />
                    </div>
                    <div className="col col-md-4">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th scope="col"></th>
                                    <th scope="col"><h3>Scores</h3></th>
                                    <th scope="col"></th>
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
                        <HandCards gameState = { this.state.gameState } playerState = { this.state.playerState } />
                    </ul>
                </div>
            </React.Fragment>
        )
    }
}

ReactDOM.render(
    <Root />,
    document.getElementById('root')
);
