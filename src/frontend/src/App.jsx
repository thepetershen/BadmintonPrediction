import SearchComponent from "./SearchComponent.jsx"
import {useState} from 'react'

function App() {
  const [winnerInfo, setWinnerInfo] = useState({});

  return (
    <>
      <SearchComponent setWinnerInfo = {setWinnerInfo}/>
    </>
  )
}

export default App
