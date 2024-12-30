const VIEWING_DISTANCE_MM = 350; // 35cm
const REFERENCE_DISTANCE_MM = 4000; // 4m
const SIZE_RATIO = VIEWING_DISTANCE_MM / REFERENCE_DISTANCE_MM;
const BASE_SIZE_MM = 8.73; // Standard size for 20/20 vision at 4m
let currentTestIndex = 0;
let incorrectAnswers = 0;
let highestLevelPassed = 1;
let currentEye = "Left";
let leftEyeLevel = 0;
let rightEyeLevel = 0;
let rightEyeIncorrect = 0;
let leftEyeIncorrect = 0;
let feedBack = "";
let testInProgress = false;
let tests = generateTestLevels();

function calculateLandoltCSize(level, calibrationData) {
  // Get physical screen dimensions from calibration
  const screenWidthMM = calibrationData.screenWidth;
  const screenHeightMM = calibrationData.screenHeight;
  
  // Calculate base size
  const sizeAtLevel = BASE_SIZE_MM * Math.pow(1.2589, 17 - level);
  const adjustedSize = sizeAtLevel * SIZE_RATIO;
  
  // Screen size constraint factor
  const screenSizeFactor = Math.min(screenWidthMM, screenHeightMM) / 400; // 400mm as reference
  
  // Convert to pixels with all factors
  const dpi = window.devicePixelRatio * 96;
  const pixelsPerMM = dpi / 25.4;
  const distanceAdjustment = calibrationData.measuredDistance / VIEWING_DISTANCE_MM;
  
  return Math.round(adjustedSize * pixelsPerMM * distanceAdjustment * screenSizeFactor);
}

function generateTestLevels() {
  const levels = [];
  for (let level = 1; level <= 17; level++) {
    const rotation = Math.floor(Math.random() * 8) * 45;
    levels.push({
      level: level,
      rotation: rotation,
      correctAnswer: String(((rotation / 45) + 1) % 8 || 8),
      width: "50px"
    });
  }
  return levels;
}

function loadTest() {
  const calibrationData = JSON.parse(localStorage.getItem('screenCalibration'));
  if (!calibrationData) {
      window.location.href = '/calibration';
      return;
  }

  if (incorrectAnswers >= 3 || currentTestIndex >= tests.length) {
      if (currentEye === "Left") {
          leftEyeLevel = highestLevelPassed;
          leftEyeIncorrect = incorrectAnswers;
          const coverEyeMessage = document.getElementById("cover-eye-message");
          if (coverEyeMessage) {
              coverEyeMessage.style.display = "flex";
              coverEyeMessage.style.opacity = "1";
          }
          return;
      } else {
          endTest();
          return;
      }
  }

  const test = tests[currentTestIndex];
  const littleCircle = document.querySelector(".littleCircle");
  const errorMessage = document.getElementById("error-message");
  errorMessage.style.display = "none";
  
  // Calculate size using calibration
  const size = calculateLandoltCSize(test.level, calibrationData);
  littleCircle.style.width = `${size}px`;
  littleCircle.style.height = `${size}px`; // Add height
  littleCircle.style.transform = `rotate(${test.rotation}deg)`;
//  console.log(`Level ${test.level}: Size=${size}px, Rotation=${test.rotation}°`); // Debug log
  const levelDisplay = document.getElementById("current-level");
  if (levelDisplay) {
      levelDisplay.textContent = `Current Level: ${test.level}`;
  }

  document.querySelectorAll("svg path.part").forEach(path => {
      path.onclick = (event) => handleClick(event);
  });
}

function handleCoverEyeOK() {
  const coverEyeMessage = document.getElementById("cover-eye-message");
  
  if (coverEyeMessage) {
      coverEyeMessage.style.opacity = "0";
      
      setTimeout(() => {
          coverEyeMessage.style.display = "none";
          
          // Reset for right eye test
          leftEyeIncorrect = incorrectAnswers;
          currentTestIndex = 0;
          incorrectAnswers = 0;
          highestLevelPassed = 1;
          currentEye = "Right";
          tests = generateTestLevels(); // Generate new tests for right eye

          document.getElementById("instructions").innerText = 
              "I)Please cover your right eye!\nII)Keep your head in a distance of 30-35 cm from the screen!\nIII)Find the gap and mark it on the lower ring!";

          const currentEyeDisplay = document.getElementById("current-eye");
          if (currentEyeDisplay) {
              currentEyeDisplay.textContent = `Current Eye: Right Eye`;
          }

          loadTest();
      }, 500);
  }
}
function handleClick(event) {
 const test = tests[currentTestIndex];
 const clickedId = event.target.id;
 const errorMessage = document.getElementById("error-message");

 if (clickedId === test.correctAnswer) {
   currentTestIndex += test.level <= 10 ? 2 : 1;
   highestLevelPassed = Math.max(highestLevelPassed, test.level);
   loadTest();
 } else {
   incorrectAnswers++;
   
   if (incorrectAnswers >= 3) {
     errorMessage.textContent = "Maximum incorrect answers reached.";
     errorMessage.style.display = "block";

     if (currentEye === "Left") {
       leftEyeLevel = highestLevelPassed;
       const coverEyeMessage = document.getElementById("cover-eye-message");
       coverEyeMessage.style.display = "flex";
       coverEyeMessage.style.opacity = "1";
       
       const okButton = document.getElementById("ok-button");
       if (okButton) {
         okButton.removeEventListener("click", handleCoverEyeOK);
         okButton.addEventListener("click", handleCoverEyeOK);
       }
     } else {
       endTest();
     }
     return;
   }

   errorMessage.textContent = "Wrong answer! Be careful.";
   errorMessage.style.display = "block";
   currentTestIndex = Math.max(0, currentTestIndex - 1);
   loadTest();
 }
}

function startTest() {
 const testControls = document.getElementById("test-controls");
 const testArea = document.getElementById("test-area");

 testControls.style.display = "none";
 testArea.style.display = "block";

 currentTestIndex = 0;
 incorrectAnswers = 0;
 highestLevelPassed = 1;
 currentEye = "Left";
 tests = generateTestLevels();

 const currentEyeDisplay = document.getElementById("current-eye");
 currentEyeDisplay.textContent = `Current Eye: Left Eye`;
 
 testInProgress = true;
 window.addEventListener("beforeunload", confirmNavigation);
 loadTest();
}

function confirmNavigation(event) {
 if (testInProgress) {
   event.preventDefault();
   event.returnValue = '';
 }
}

function endTest() {
 const errorMessage = document.getElementById("error-message");
 const feedbackMessage = document.createElement("div");
 feedbackMessage.style.cssText = "margin-top: 20px; font-size: 1.2rem; font-weight: bold;";

 if (currentEye === "Right") {
   rightEyeLevel = highestLevelPassed;
   rightEyeIncorrect = incorrectAnswers;
 }

 let visionFeedback = determineVisionFeedback(leftEyeLevel, rightEyeLevel);
 feedbackMessage.innerHTML = visionFeedback.message;
 feedbackMessage.style.color = visionFeedback.color;

 const testArea = document.getElementById("test-area");
 const instructionsArea = document.getElementById("instructions");
 
 if (testArea) testArea.style.display = "none";
 if (instructionsArea) instructionsArea.style.display = "none";

 const contentContainer = document.querySelector(".content-container");
 contentContainer.appendChild(feedbackMessage);

 const okButton = document.createElement("button");
 okButton.textContent = "OK";
 okButton.style.cssText = `
   margin-top: 20px;
   padding: 10px 20px;
   font-size: 1rem;
   cursor: pointer;
   background-color: #4CAF50;
   color: white;
   border: none;
   border-radius: 5px;
 `;

 contentContainer.appendChild(okButton);
 
 okButton.addEventListener("click", () => {
   window.removeEventListener("beforeunload", confirmNavigation);
   contentContainer.innerHTML = "";

   const savingResultsMessage = document.createElement("div");
   savingResultsMessage.id = "saving-results-message";
   savingResultsMessage.style.cssText = `
     margin-top: 20px;
     font-size: 1.5rem;
     font-weight: bold;
     color: #337ab7;
   `;
   savingResultsMessage.textContent = "Saving results...";
   contentContainer.appendChild(savingResultsMessage);

   saveTestResult();
   setTimeout(() => {
     window.location.href = "allTests";
   }, 2200);
 });
}

document.addEventListener("DOMContentLoaded", function() {
 const startTestBtn = document.getElementById("start-test-btn");
 if (startTestBtn) {
   startTestBtn.addEventListener("click", startTest);
 }

 const okButton = document.getElementById("okButton");
 if (okButton) {
   okButton.addEventListener("click", function() {
     document.getElementById("title").innerText = "Visual Acuity Test";
     document.getElementById("instructions").innerText = "I)Please cover your left eye!\nII)Keep your head in a distance of 30-35 cm from the screen!\nIII)Find the gap and mark it on the lower ring!";

     const testControls = document.getElementById("test-controls");
     const testArea = document.getElementById("test-area");
     testControls.style.display = "none";
     testArea.style.display = "block";

     startTest();
     window.addEventListener('beforeunload', confirmNavigation);
   });
 }

 const coverEyeOkButton = document.getElementById("ok-button");
 if (coverEyeOkButton) {
   coverEyeOkButton.addEventListener("click", handleCoverEyeOK);
 }
});

function determineVisionFeedback(leftEye, rightEye) {
  const averageLevel = Math.floor((leftEye + rightEye) / 2);
  let feedback = { message: "", color: "" };

  if (averageLevel < 5) {
      feedback.message = "Your vision seems too low! You should visit an eye doctor immediately.";
      feedback.color = "#d9534f";
  } else if (averageLevel <= 10) {
      feedback.message = "Your vision needs attention. We recommend scheduling a visit to an eye doctor.";
      feedback.color = "#f0ad4e";
  } else if (averageLevel <= 13) {
      feedback.message = "Your vision is okay, but consider an eye checkup for better clarity.";
      feedback.color = "#f0ad4e";
  } else {
      feedback.message = "Great! Your vision seems excellent. Keep maintaining eye health.";
      feedback.color = "#5cb85c";
  }

  feedBack = feedback.message;
  feedback.message += `<br>Left Eye Level: ${leftEye}/17<br>Right Eye Level: ${rightEye}/17`;
  return feedback;
}

function saveTestResult() {
 const resultData = {
   leftEyeLevel,
   rightEyeLevel,
   incorrectAnswers,
   rightEyeIncorrect,
   leftEyeIncorrect,
   feedBack
 };
 
 fetch("/Visual_Acuity_save_results", {
   method: "POST",
   headers: {
     "Content-Type": "application/json",
   },
   body: JSON.stringify(resultData)
 })
 .then(response => response.json())
 .then(data => {
   if (data.success) {
     console.log("Test results saved successfully.");
   } else {
     console.log("Error saving test results.");
   }
 })
 .catch(error => console.error("Error:", error));
}