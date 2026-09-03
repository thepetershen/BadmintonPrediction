import SearchComponent from "./SearchComponent.jsx"
import ExpectedWinnerComponent from "./ExpectedWinnerComponent.jsx"
import {useState} from 'react'
import './App.css'

function App() {
  const [winnerInfo, setWinnerInfo] = useState({"player1_name": "", "player2_name": "", "prediction": 0 });

  return (
    <div className="app">
      <div className="app-header">
        <h1>
          Badminton Match Result Predictor
        </h1>
        <p>
          Hey! Welcome to Badminton Match Result Predictor. This site aggregated publicly availible badminton match data to train several models in order to predict the result of a badminton match.
          It is trained upon matches from Super 300 and above events from 2022 - 2026 (post pandemic).
          Try out the model!
          This project is also open sourced! https://github.com/thepetershen/BadmintonPrediction
        </p>
      </div>
      <SearchComponent setWinnerInfo = {setWinnerInfo}/>
      <ExpectedWinnerComponent winnerInfo = {winnerInfo}/>
    </div>
  )
}

export default App
