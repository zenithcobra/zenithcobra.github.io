$(document).ready(function () {
    // Resize the grid to fit the window on load
    function resizeGrid() {
        const gridSize = $(window).height() * 0.50;
        $('table').css({ width: gridSize + 'px', height: gridSize + 'px' });
    }

    resizeGrid();

    // Resize the grid dynamically when the window is resized
    $(window).on('resize', resizeGrid);

    // Show and hide instructions
    $('#info').click(function () {
        $('#instruct').css({ display: 'block' });
    });

    $('#close').click(function () {
        $('#instruct').css({ display: 'none' });
    });

    $('#resultclose').click(function () {
        $('#resultswindow').css({ display: 'none' });
    });

    // Define audio for letters
    const sounds = {
        b: new Howl({ src: ['audio/b.mp3'] }),
        f: new Howl({ src: ['audio/f.mp3'] }),
        k: new Howl({ src: ['audio/k.mp3'] }),
        n: new Howl({ src: ['audio/n.mp3'] }),
        p: new Howl({ src: ['audio/p.mp3'] }),
        q: new Howl({ src: ['audio/q.mp3'] }),
        r: new Howl({ src: ['audio/r.mp3'] }),
        t: new Howl({ src: ['audio/t.mp3'] }),
    };

    // Game variables
    let n = 2; // Initial N value
    let userScore = [0, 0, 0, 0]; // Visual correct, audio correct, visual mistakes, audio mistakes
    let blockRunning = false;

    // Prepare a block of N-Back data
    function prepareBlock(n) {
        const block = [];
        const blockLength = 20 + n;

        // Initialize the block with empty pairs
        for (let i = 0; i < blockLength; i++) {
            block.push([0, 0]);
        }

        // Add visual and audio targets
        const addTargets = (typeIndex, targetCount) => {
            let count = 0;
            while (count < targetCount) {
                const targetIndex = Math.floor(Math.random() * blockLength);
                if (
                    block[targetIndex][typeIndex] === 0 &&
                    block[targetIndex + n] &&
                    block[targetIndex + n][typeIndex] === 0
                ) {
                    const value = 1 + Math.floor(Math.random() * 8);
                    block[targetIndex][typeIndex] = value;
                    block[targetIndex + n][typeIndex] = value;
                    count++;
                }
            }
        };

        addTargets(0, 4); // Add 4 visual targets
        addTargets(1, 4); // Add 4 audio targets

        return block;
    }

    // Evaluate the block for correctness
    function evaluateBlock(block) {
        let visualTargets = 0;
        let audioTargets = 0;

        for (let i = n; i < block.length; i++) {
            if (block[i][0] === block[i - n][0]) visualTargets++;
            if (block[i][1] === block[i - n][1]) audioTargets++;
        }

        return [visualTargets, audioTargets];
    }

    // Play a square on the grid
    function playSquare(squareIndex) {
        const squareIds = ['uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve'];
        const squareId = squareIds[squareIndex - 1];
        if (squareId) {
            $(`#${squareId}`).toggleClass('on');
            setTimeout(() => $(`#${squareId}`).toggleClass('on'), 500);
        }
    }

    // Play a letter sound
    function playLetter(letterIndex) {
        const letters = ['b', 'f', 'k', 'n', 'p', 'q', 'r', 't'];
        const letter = letters[letterIndex - 1];
        if (letter && sounds[letter]) {
            sounds[letter].play();
        }
    }

    // Main game function
    function playBlock() {
        const block = prepareBlock(n);
        const blockLength = block.length;
        let blockCounter = 0;
        let hits = [0, 0]; // Tracks user hits for visual and audio

        function playNext() {
            if (blockCounter < blockLength) {
                const [visual, audio] = block[blockCounter];

                // Play visual and audio cues
                if (visual) playSquare(visual);
                if (audio) playLetter(audio);

                // Listen for user input
                $(document).off('keydown').on('keydown', (event) => {
                    if (event.key === 'a') hits[0] = 1; // Visual match
                    if (event.key === 'l') hits[1] = 1; // Audio match
                });

                // Evaluate user input after the cue
                setTimeout(() => {
                    if (blockCounter >= n) {
                        const [prevVisual, prevAudio] = block[blockCounter - n];
                        if (visual === prevVisual) {
                            if (hits[0]) userScore[0]++;
                            else userScore[2]++;
                        } else if (hits[0]) {
                            userScore[2]++;
                        }

                        if (audio === prevAudio) {
                            if (hits[1]) userScore[1]++;
                            else userScore[3]++;
                        } else if (hits[1]) {
                            userScore[3]++;
                        }
                    }

                    hits = [0, 0]; // Reset hits
                    blockCounter++;
                    playNext(); // Play the next cue
                }, 3000); // Wait 3 seconds before the next cue
            } else {
                // End of block
                $('#resultswindow').css({ display: 'block' });
                $('#results').html(
                    `You got ${userScore[0]} of 6 visual cues and ${userScore[1]} of 6 audio cues.`
                );

                if (userScore[2] < 3 && userScore[3] < 3) {
                    n++;
                    $('#resultstwo').html(`Great job! N has been increased to ${n}.`);
                } else if (userScore[2] + userScore[3] > 6) {
                    if (n > 1) n--;
                    $('#resultstwo').html(`You made too many mistakes. N has been decreased to ${n}.`);
                } else {
                    $('#resultstwo').html(`N will remain ${n}.`);
                }

                $('#nvalue').html(`n = ${n}`);
                userScore = [0, 0, 0, 0]; // Reset score
            }
        }

        playNext(); // Start the block
    }

    // Start the game when the "Begin" button is clicked
    $('#begin').click(function () {
        if (!blockRunning) {
            blockRunning = true;
            playBlock();
            setTimeout(() => (blockRunning = false), 20000); // Prevent multiple blocks from running simultaneously
        }
    });
});