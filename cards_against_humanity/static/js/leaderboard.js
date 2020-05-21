class Leaderboard extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            players: []
        };
    }

    // function which is called when component is added
    componentDidMount() {
        // get players
        this.fetchPlayers()
        this.timer = setInterval(() => this.fetchPlayers(), 5000);
    }

    // function which is called when component about to be removed
    componentWillUnmount() {
        clearInterval(this.timer);
        this.timer = null;
    }

    fetchPlayers() {
        this.setState({players: this.state.players});
        // Make a request for players for this game
        axios.get('/api/' + getCookie("game_id") + '/get_players')
        .then(response => {
            // handle success
            this.setState({players: response.data})
        })
        .catch(error => {
            // handle error
            console.log(error);
            this.setState({players: this.state.players})
        });
    }

    render() {
        return (
            this.state.players.map((player) =>
            <tr key={ player.id }>
                <td>{(() => {
                    switch (player.state) {
                        case 0: return "\u{274C}";
                        case 1: return "\u{2714}";
                        case 2: return "\u{1F451}";
                        default: return "";
                    }
                })()}</td>
                <td>{ player.name }</td>
                <td>{ player.score }</td>
            </tr>
            )
        )
    }
}
