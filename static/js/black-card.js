class BlackCard extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            text: this.props.text
        };
    }
    render() {
        if (this.props.gameState == 0) {
            return <h4>Waiting for card tzar to pick a card...</h4>
        } else if (this.props.gameState == 1) {
            return (
                <div className="card black-card float-right">
                    <div className="card-body">
                        <h5 className="card-title">{ this.state.text }</h5>
                    </div>
                </div>
            )
        } else {
            return (
                <div id="black-card" className="col col-md-4">
                    <h1>Error!</h1>
                </div>
            )
        }
    }
}