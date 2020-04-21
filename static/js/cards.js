const cardData = [{_id: "1", text: "Card 1"}, {_id: "2", text: "Card 2"}, {_id: "3", text: "Card 3"}];
const cards = cardData.map((card) =>
    <li key={card._id}>
        <div className="card hand-card" data-cardid="{{ card._id }}" onClick={(e) => this.playCard(id, e)}>
            <div className="card-body">
                <h5 className="card-title">{card.text}</h5>
            </div>
        </div>
    </li>
);

class HandCards extends React.Component {

    constructor(props) {
        super(props);
        this.state = {cards: "Test"};
    }

    playCard() {
        alert("test");
    }

    render() {
        return (
            <ul className="cards">{cards}</ul>
        );
    }
}

ReactDOM.render(
    <HandCards />,
    document.getElementById('hand-cards')
);
