class Leaderboard extends React.Component {

    constructor(props) {
        super(props);
        this.state = {users: "Alex 2"};
    }

    // function which is called when component is added
    componentDidMount() {
        this.timerID = setInterval(
            () => this.tick(),
            1000
        );
    }

    // function which is called when component about to be removed
    componentWillUnmount() {
        clearInterval(this.timerID);
    }

    tick() {
        this.setState({
            users: "Peter 3"
        });
    }

    render() {
        return (
            <li>{this.state.users}</li>
        );
    }
}

ReactDOM.render(
    <Leaderboard />,
    document.getElementById('leaderboard')
);
