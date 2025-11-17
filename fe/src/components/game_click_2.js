// Emotion data
const eyebrowOptions = [{
        svgLeft: 'M 20 15 Q 50 10 80 15',
        svgRight: 'M 20 15 Q 50 10 80 15',
        label: 'Happy'
    },
    {
        svgLeft: 'M 20 20 Q 50 25 80 20',
        svgRight: 'M 20 20 Q 50 25 80 20',
        label: 'Sad'
    },
    {
        svgLeft: 'M 80 20 L 20 10',
        svgRight: 'M 20 20 L 80 10',

        label: 'Angry'
    },
    {
        svgLeft: 'M 20 10 Q 50 5 80 10',
        svgRight: 'M 20 10 Q 50 5 80 10',
        label: 'Surprised'
    },
    {
        svgLeft: 'M 20 15 Q 50 20 80 15',
        svgRight: 'M 20 15 Q 50 20 80 15',
        label: 'Worried'
    }
];

const eyeOptions = [{
        type: 'circle',
        label: 'Happy',
        r: 15
    },
    {
        type: 'ellipse',
        label: 'Sad',
        rx: 15,
        ry: 12
    },
    {
        type: 'circle',
        label: 'Angry',
        r: 12
    },
    {
        type: 'circle',
        label: 'Surprised',
        r: 20
    },
    {
        type: 'circle',
        label: 'Excited',
        r: 18
    },
    {
        type: 'ellipse',
        label: 'Scared',
        rx: 18,
        ry: 22
    }
];

const lipOptions = [{
        type: 'teeth',
        label: 'Smile'
    },
    {
        svg: 'M 20 60 Q 50 40 80 60',
        label: 'Frown'
    },
    {
        svg: 'M 20 50 L 80 50',
        label: 'Straight'
    },
    {
        type: 'surprise',
        label: 'Open'
    },
    {
        svg: 'M 20 45 Q 50 75 80 45',
        label: 'Big Smile'
    },
    {
        svg: 'M 25 50 Q 50 60 75 50',
        label: 'Small O'
    }
];

const situations = [{
        text: "It's your birthday and you got a puppy! 🎁",
        emoji: '🎉',
        emotion: 'happy',
        eyebrows: 0,
        eyes: 0,
        lips: 0
    },
    {
        text: 'Your ice cream fell on the ground! 🍦',
        emoji: '😢',
        emotion: 'sad',
        eyebrows: 1,
        eyes: 1,
        lips: 1
    },
    {
        text: 'Someone took your favorite toy without asking! 🧸',
        emoji: '😠',
        emotion: 'angry',
        eyebrows: 2,
        eyes: 2,
        lips: 2
    },
    {
        text: 'You opened a present and found exactly what you wanted! 🎁',
        emoji: '😲',
        emotion: 'surprised',
        eyebrows: 3,
        eyes: 3,
        lips: 3
    },
    {
        text: "It's time to go to the park and play! 🎈",
        emoji: '🤩',
        emotion: 'excited',
        eyebrows: 0,
        eyes: 4,
        lips: 4
    },
    {
        text: 'You heard a strange noise in the dark! 🌙',
        emoji: '😨',
        emotion: 'scared',
        eyebrows: 4,
        eyes: 5,
        lips: 5
    },
    {
        text: 'Your friend shared their candy with you! 🍬',
        emoji: '😊',
        emotion: 'happy',
        eyebrows: 0,
        eyes: 0,
        lips: 0
    },
    {
        text: 'You have to leave the playground when you were having fun! 🛝',
        emoji: '☹️',
        emotion: 'sad',
        eyebrows: 1,
        eyes: 1,
        lips: 1
    }
];

// Game state
let currentQuestion = 0;
let selectedEyebrows = 0;
let selectedEyes = 0;
let selectedLips = 0;
let score = 0;
let questionsAnswered = 0;
let showingFeedback = false;

// DOM elements
const questionNumber = document.getElementById('questionNumber');
const scoreElement = document.getElementById('score');
const situationEmoji = document.getElementById('situationEmoji');
const situationText = document.getElementById('situationText');
const feedbackCorrect = document.getElementById('feedbackCorrect');
const feedbackIncorrect = document.getElementById('feedbackIncorrect');
const eyebrowBtn = document.getElementById('eyebrowBtn');
const eyesBtn = document.getElementById('eyesBtn');
const lipsBtn = document.getElementById('lipsBtn');
const eyebrowLabel = document.getElementById('eyebrowLabel');
const eyesLabel = document.getElementById('eyesLabel');
const lipsLabel = document.getElementById('lipsLabel');
const resetBtn = document.getElementById('resetBtn');
const checkBtn = document.getElementById('checkBtn');
const skipBtn = document.getElementById('skipBtn');
const leftEyebrow = document.getElementById('leftEyebrow');
const rightEyebrow = document.getElementById('rightEyebrow');
const leftEye = document.getElementById('leftEye');
const rightEye = document.getElementById('rightEye');
const mouth = document.getElementById('mouth');

// Initialize game
function init() {
    updateSituation();
    updateFace();
    updateLabels();
    updateStats();

    // Event listeners
    eyebrowBtn.addEventListener('click', () => {
        if (!showingFeedback) {
            selectedEyebrows = (selectedEyebrows + 1) % eyebrowOptions.length;
            updateFace();
            updateLabels();
        }
    });

    eyesBtn.addEventListener('click', () => {
        if (!showingFeedback) {
            selectedEyes = (selectedEyes + 1) % eyeOptions.length;
            updateFace();
            updateLabels();
        }
    });

    lipsBtn.addEventListener('click', () => {
        if (!showingFeedback) {
            selectedLips = (selectedLips + 1) % lipOptions.length;
            updateFace();
            updateLabels();
        }
    });

    resetBtn.addEventListener('click', resetFace);
    checkBtn.addEventListener('click', checkAnswer);
    skipBtn.addEventListener('click', skipQuestion);
}

// Update situation
function updateSituation() {
    const situation = situations[currentQuestion];
    situationEmoji.textContent = situation.emoji;
    situationText.textContent = situation.text;

    // Add fade in animation
    situationEmoji.classList.remove('fade-in');
    void situationEmoji.offsetWidth; // Trigger reflow
    situationEmoji.classList.add('fade-in');
}

// Update face
function updateFace() {
    // Update eyebrows
    // const eyebrow = eyebrowOptions[selectedEyebrows];
    // leftEyebrow.innerHTML = `
    //     <path d="${eyebrow.svg}" transform="translate(65, 95)" 
    //           stroke="#6B4423" stroke-width="5" fill="none" stroke-linecap="round" />
    // `;
    // rightEyebrow.innerHTML = `
    //     <path d="${eyebrow.svg}" transform="translate(175, 95)" 
    //           stroke="#6B4423" stroke-width="5" fill="none" stroke-linecap="round" />
    // `;
    const eyebrow = eyebrowOptions[selectedEyebrows];

    leftEyebrow.innerHTML = `
        <path d="${eyebrow.svgLeft}" 
            transform="translate(45, 95)"
            fill="none" stroke="#6B4423" stroke-width="5"
            stroke-linecap="round" />
    `;

    rightEyebrow.innerHTML = `
        <path d="${eyebrow.svgRight}" 
            transform="translate(160, 95)"
            fill="none" stroke="#6B4423" stroke-width="5"
            stroke-linecap="round" />
    `;


    // Update eyes
    const eye = eyeOptions[selectedEyes];
    if (eye.type === 'circle') {
        leftEye.innerHTML = `
            <circle cx="105" cy="135" r="${eye.r}" fill="white" stroke="#333" stroke-width="2.5" />
            <circle cx="105" cy="135" r="${eye.r * 0.6}" fill="#8B4513" />
            <circle cx="105" cy="135" r="${eye.r * 0.35}" fill="#000" />
            <circle cx="108" cy="132" r="${eye.r * 0.2}" fill="white" />
            <path d="M 100 120 Q 105 118 110 120" stroke="#333" stroke-width="1.5" fill="none" />
        `;
        rightEye.innerHTML = `
            <circle cx="195" cy="135" r="${eye.r}" fill="white" stroke="#333" stroke-width="2.5" />
            <circle cx="195" cy="135" r="${eye.r * 0.6}" fill="#8B4513" />
            <circle cx="195" cy="135" r="${eye.r * 0.35}" fill="#000" />
            <circle cx="198" cy="132" r="${eye.r * 0.2}" fill="white" />
            <path d="M 190 120 Q 195 118 200 120" stroke="#333" stroke-width="1.5" fill="none" />
        `;
    } else {
        leftEye.innerHTML = `
            <ellipse cx="105" cy="135" rx="${eye.rx}" ry="${eye.ry}" 
                     fill="white" stroke="#333" stroke-width="2.5" />
            <circle cx="105" cy="135" r="8" fill="#8B4513" />
            <circle cx="105" cy="135" r="5" fill="#000" />
            <circle cx="107" cy="133" r="2" fill="white" />
            <path d="M 100 120 Q 105 118 110 120" stroke="#333" stroke-width="1.5" fill="none" />
        `;
        rightEye.innerHTML = `
            <ellipse cx="195" cy="135" rx="${eye.rx}" ry="${eye.ry}" 
                     fill="white" stroke="#333" stroke-width="2.5" />
            <circle cx="195" cy="135" r="8" fill="#8B4513" />
            <circle cx="195" cy="135" r="5" fill="#000" />
            <circle cx="197" cy="133" r="2" fill="white" />
            <path d="M 190 120 Q 195 118 200 120" stroke="#333" stroke-width="1.5" fill="none" />
        `;
    }

    // Update mouth
    const lips = lipOptions[selectedLips];
    if (lips.type === 'teeth') {
        // Miệng cười nhe răng cho happy
        mouth.innerHTML = `
            <g transform="translate(108, 155)">
            
                <path d="M 5 55 Q 45 85 85 55"
                  stroke="#D14D72"
                  stroke-width="7"
                  fill="none"
                  stroke-linecap="round" />

                <!-- Khóe miệng trái: bám vào đầu miệng, cong lên -->
                <path d="M 0 60 Q -6 54 4 48"
                    stroke="#D14D72"
                    stroke-width="7"
                    fill="none"
                    stroke-linecap="round" />

                <!-- Khóe miệng phải: đối xứng bên phải -->
                <path d="M 90 60 Q 96 54 86 48"
                    stroke="#D14D72"
                    stroke-width="7"
                    fill="none"
                    stroke-linecap="round" />

            </g>
            
        `;
    } else if (lips.type === 'surprise') {
        mouth.innerHTML = `
            <path d="${mouthData.svg}" transform="translate(90, 165)" 
                  stroke="#D14D72" stroke-width="5" fill="#8B0000" stroke-linecap="round" />
        `;
    } else {
        // Các kiểu môi còn lại giữ nguyên như cũ (chỉ là 1 đường cong)
        mouth.innerHTML = `
            <path d="${lips.svg}" transform="translate(100, 165)" 
                  stroke="#D14D72" stroke-width="5" fill="none" stroke-linecap="round" />
        `;
    }
    // mouth.innerHTML = `
    //     <path d="${lips.svg}" transform="translate(100, 165)" 
    //           stroke="#D14D72" stroke-width="5" fill="none" stroke-linecap="round" />
    // `;
}

// Update labels
function updateLabels() {
    eyebrowLabel.textContent = eyebrowOptions[selectedEyebrows].label;
    eyesLabel.textContent = eyeOptions[selectedEyes].label;
    lipsLabel.textContent = lipOptions[selectedLips].label;
}

// Update stats
function updateStats() {
    questionNumber.textContent = questionsAnswered + 1;
    scoreElement.textContent = score;
}

// Reset face
function resetFace() {
    if (!showingFeedback) {
        selectedEyebrows = 0;
        selectedEyes = 0;
        selectedLips = 0;
        updateFace();
        updateLabels();
    }
}

// Check answer
function checkAnswer() {
    if (showingFeedback) return;

    const situation = situations[currentQuestion];
    const isCorrect = selectedEyebrows === situation.eyebrows &&
        selectedEyes === situation.eyes &&
        selectedLips === situation.lips;

    showingFeedback = true;

    if (isCorrect) {
        score++;
        feedbackCorrect.classList.add('show');
        updateStats();

        setTimeout(() => {
            feedbackCorrect.classList.remove('show');
            nextQuestion();
        }, 2000);
    } else {
        feedbackIncorrect.classList.add('show');

        setTimeout(() => {
            feedbackIncorrect.classList.remove('show');
            showingFeedback = false;
        }, 1500);
    }

    updateButtonStates();
}

// Skip question
function skipQuestion() {
    if (!showingFeedback) {
        nextQuestion();
    }
}

// Next question
function nextQuestion() {
    questionsAnswered++;
    currentQuestion = (currentQuestion + 1) % situations.length;
    resetFace();
    updateSituation();
    showingFeedback = false;
    updateStats();
    updateButtonStates();
}

// Update button states
function updateButtonStates() {
    const disabled = showingFeedback;
    resetBtn.disabled = disabled;
    checkBtn.disabled = disabled;
    skipBtn.disabled = showingFeedback && feedbackCorrect.classList.contains('show');
}

// Start game
init();