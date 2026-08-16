
import './ExpectedWinnerComponent.css'

const RADIUS = 54;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

function ExpectedWinnerComponent({ winnerInfo }) {
  const { player1_name, player2_name, prediction } = winnerInfo;

  if (player1_name === "Error" || player2_name === "Error") {
    return (
      <div className="expected-winner-component expected-winner-error">
        The names provided were invalid
      </div>
    )
  } else if (player1_name === "" || player2_name === "") {
    return null;
  } else {
    console.log(winnerInfo)
    const player1WinPercent = prediction * 100;
    const winnerIsPlayer1 = prediction >= 0.5;
    const winnerName = winnerIsPlayer1 ? player1_name : player2_name;
    const confidence = Math.round(winnerIsPlayer1 ? player1WinPercent : 100 - player1WinPercent);
    const dashOffset = CIRCUMFERENCE * (1 - confidence / 100);

    return (
      <div className="expected-winner-component">
        <p className="expected-winner-headline">
          <span className="expected-winner-name">{winnerName}</span> is projected to win
        </p>
        <div className="expected-winner-ring">
          <svg viewBox="0 0 120 120" className="expected-winner-ring-svg">
            <circle className="expected-winner-ring-track" cx="60" cy="60" r={RADIUS} />
            <circle
              className="expected-winner-ring-progress"
              cx="60"
              cy="60"
              r={RADIUS}
              strokeDasharray={CIRCUMFERENCE}
              strokeDashoffset={dashOffset}
            />
          </svg>
          <div className="expected-winner-ring-label">{confidence}%</div>
        </div>
        <p className="expected-winner-subtext">confidence</p>
      </div>
    );
  }
}

export default ExpectedWinnerComponent
