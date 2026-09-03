import { useState } from 'react'
import './PlayerDropdownComponent.css'

// simple search bar component. takes in a list of valid players, and the player
// state it is going to update
function PlayerDropdownComponent({ players, player, setPlayer }) {
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)

  const filtered = players.filter((p) =>
    p.toLowerCase().includes(query.toLowerCase())
  )

  function handleSelect(name) {
    setPlayer(name)
    setQuery(name)
    setIsOpen(false)
  }

  return (
    <div className="player-dropdown">
      <input
        type="text"
        value={query}
        placeholder="Search players..."
        onChange={(e) => {
          setQuery(e.target.value)
          setIsOpen(true)
        }}
        onFocus={() => setIsOpen(true)}
        onBlur={() => setIsOpen(false)}
      />
      {isOpen && filtered.length > 0 && (
        <ul className="player-dropdown-list">
          {filtered.map((name) => (
            <li
              key={name}
              onMouseDown={() => handleSelect(name)}
            >
              {name}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default PlayerDropdownComponent
