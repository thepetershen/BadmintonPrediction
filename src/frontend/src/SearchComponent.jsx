
import { useState, useEffect } from 'react'
import PlayerDropdownComponent from './PlayerDropdownComponent.jsx';
const SERVER_API_URL = import.meta.env.VITE_API_URL

// the search componenet will contain 3 components. the two players, each with searchable fields
// and the submit bar. 
function SearchComponent() {
  // keeps track of the names of the two players
  const [player1Name, setPlayer1Name] = useState(0);
  const [player2Name, setPlayer2Name] = useState(0);
  const [playerList, setPlayerList] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => { 
    const fetchUsers = async () => {
      try {
        const response = await fetch(SERVER_API_URL + "/players");
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setPlayerList(data);
      } catch (err) {
        setError(err.message);
      }
    }
    fetchUsers();
  }, []);

  const handleClick = () => {
    alert('Button was clicked!');
  };

  return (
    <>
      <PlayerDropdownComponent 
        players = {playerList}
        player = {player1Name}
        setPlayer = {setPlayer1Name}
      />
      <PlayerDropdownComponent 
        players = {playerList}
        player = {player2Name}
        setPlayer = {setPlayer2Name}
      />
      <button type="button" onClick={handleClick}>
        Submit
      </button>
    </>
  )
}

export default SearchComponent
