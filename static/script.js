let questions = [];
let currentQuestion = 0;
let score = 0;
let selectedCategory = "Mixed";
let playerName = "Guest";
let answerLocked = false;

const challengeCard = document.querySelector(".challenge-card");

async function startQuiz(category = "Mixed") {
    selectedCategory = category;
    currentQuestion = 0;
    score = 0;
    answerLocked = false;

    try {
        let url = "/api/questions";

        if (category !== "Mixed") {
            url += "?category=" + encodeURLComponent(category);
        }

        const response = await fetch(url);

        if (response.ok) {
            throw new Error("Questions could not be loaded.");
        }

        questions = await response.json();

        if (questions.length === 0) {
            challengeCard.innerHTML = `
            <h2> No Questions Available </h2>
            <p> Please try another category.</p>`;
                return;
                    }

        showQuestion();

                
    } catch (error) {
        challengeCard.innerHTML = `
        <h2> Something Went wrong! </h2>
        <p> $(error.message)</p>`;

        console.error(error);

    }
}

function showQuestion() {
    answerLocked = false;

    const question = questions[currentQuestion];

    const options = [
        question.option_a,
        question.option_b,
        question.option_c
    ];

    challengeCard.innerHTML = `
    <div class="challenge-top">
    <span> DAILY CHALLENGE </span>
    <span> $(currentQuestion + 1)/${questions.length}</span>
    </div>
    
    <h2 class = "question">${question.question}</h2>
    
    <div class="answer-option">
    ${options.map((option, index) => `
        <button class = "answer-option"
        onclick = "checkAnswer(${question.id},${index}, this)">
        ${option}
        </button>
        `).join("")}
            </div>
            <p class="challenge-note" id="feedback"></p>
     `;
}

async function checkAnswer(questionId, selectedAnswer,button) {
    if (answerLocked) return;

    answerLocked = true;

    try {
        const response = await fetch("/api/check-answer", {
            method : "POST",
            headers: {
                "Content-Type" : "application/json"

            },
            body : JSON.stringify ({
                question_id : questionId,
                selected_answer : selectedAnswer
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Answer verification failed");

        }

        const feedback = document.querySelector("#feedback");


        if (result.correct) {
            score ++;
            button.classList.add("correct");
            feedback.textContent = "Correct" + result.explanation;

    }   else { 
        button.classList.add("incorrect");
        feedback.textContent = "Incorrect!" + result.explanation;
        }

        document.querySelectorAll(".answer-option").forEach(option => {
            option.disabled = true;

        });

        const nextButton = document.createElement("button");

        nextButton.className = "next-button";
        nextButton.textContent = 
        currentQuestion === questionId,length - 1?"see Result"
        : "Next Question";

        nextButton.onclick = nextQuestion;

        challengeCard.appendChild(nextButton);

    } catch (error) {
        answerLocked = false;
        document.querySelector("#feedback").textContent = error.message;
    }
}


function nextQuestion() {
    currentQuestion++;

    if (currentQuestion < questions.length) {
        showQuestion ();
    } else{
        showResult();
    }
}


async function showResult() {
    challengeCard.innerHTML = `
    <div class="challenge-top">
    QUIZ COMPLETED
    </div>
    
    <h2 class="result-title">
    Your Score : ${score}/${questions.length}
    </h2>
    
    <P> Great Effort ! Keep learning and practising. </p>
    
    <button class="next-button" onclick = "startQuiz(selectedCategory)">
    Try Again
    </button.
    `;


    try {
        const response = await fetch("/api/results", 
            {
                method : "POST",
                headers: {
                    "Content-Type" : "application/json"
                },

                body : JSON.stringify({
                    player_name : playerName,
                    category : selectedCategory,
                    score :score,
                    total_questions : questions.length

                })
            }
        );

        if (!response.ok) {
            console.error("Result could not be saved");
        }
    } catch (error) {
        console.error("Error saving result : ",error);

        }
    }

document.addEventListener (
    "DOMContentLoaded", () =>
    {
        startQuiz();
    });