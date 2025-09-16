(function (window, document) {
  'use strict';

  // Selectors
  const modalOverlay = document.getElementById('modal-overlay');
  const modalBody = document.querySelector('.modal-body #inline-content');
  const nBackTrigger = document.querySelector('a[data-action="n-back-game"]');

  // Game Variables
  let sequence = [];
  let userResponses = [];
  let currentIndex = 0;
  let n = 2; // Default N value for N-Back
  let gameInterval;

  // Open the modal
  function openModal() {
    modalOverlay.hidden = false;
    modalOverlay.style.display = 'block';
  }

  // Close the modal
  function closeModal() {
    modalOverlay.hidden = true;
    modalOverlay.style.display = 'none';
    clearInterval(gameInterval); // Stop the game when the modal is closed
  }

  // Generate a random letter
  function generateRandomLetter() {
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    return letters[Math.floor(Math.random() * letters.length)];
  }

  // Start the N-Back game
  function startNBackGame() {
    sequence = [];
    userResponses = [];
    currentIndex = 0;

    // Clear the modal content and add game instructions
    modalBody.innerHTML = `
      <h2>N-Back Game</h2>
      <p>Press "Match" if the current letter matches the one ${n} steps back.</p>
      <div id="game-area" style="font-size: 2em; text-align: center; margin: 20px 0;"></div>
      <div style="text-align: center;">
        <button id="match-button" class="button">Match</button>
        <button id="close-game-button" class="button">Close</button>
      </div>
    `;

    const gameArea = document.getElementById('game-area');
    const matchButton = document.getElementById('match-button');
    const closeGameButton = document.getElementById('close-game-button');

    // Close the game when the "Close" button is clicked
    closeGameButton.addEventListener('click', closeModal);

    // Handle "Match" button clicks
    matchButton.addEventListener('click', () => {
      if (currentIndex >= n && sequence[currentIndex] === sequence[currentIndex - n]) {
        userResponses.push(true);
        alert('Correct!');
      } else {
        userResponses.push(false);
        alert('Incorrect!');
      }
    });

    // Start the game loop
    gameInterval = setInterval(() => {
      const randomLetter = generateRandomLetter();
      sequence.push(randomLetter);
      gameArea.textContent = randomLetter;
      currentIndex++;
    }, 2000); // Show a new letter every 2 seconds
  }

  // Initialize the N-Back game when the article is clicked
  function initNBackGame() {
    nBackTrigger.addEventListener('click', (event) => {
      event.preventDefault(); // Prevent default link behavior
      openModal();
      startNBackGame();
    });
  }

  // Run the initialization on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNBackGame);
  } else {
    initNBackGame();
  }
})(window, document);