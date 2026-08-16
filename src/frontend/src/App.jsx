import SearchComponent from "./SearchComponent.jsx"
import ExpectedWinnerComponent from "./ExpectedWinnerComponent.jsx"
import {useState} from 'react'

function App() {
  const [winnerInfo, setWinnerInfo] = useState({"player1_name": "", "player2_name": "", "prediction": 0 });

  return (
    <>
      <SearchComponent setWinnerInfo = {setWinnerInfo}/>
      <ExpectedWinnerComponent winnerInfo = {winnerInfo}/>
    </>
  )
}

export default App
