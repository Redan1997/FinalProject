let distance = null;
let screenParams = null;
let faceDetected = false;
let calibrationInProgress = false;
let modelLoaded = false;

document.addEventListener('DOMContentLoaded', function() {
    const goBackButton = document.getElementById('GoBack');
    const calibrationArea = document.getElementById('calibration-area');

    // Initialize screen parameters
    screenParams = {
        width: window.screen.width,
        height: window.screen.height,
        pixelRatio: window.devicePixelRatio,
        // Convert logical pixels to physical mm (approximate)
        physicalWidth: window.screen.width / window.devicePixelRatio * 0.264583,
        physicalHeight: window.screen.height / window.devicePixelRatio * 0.264583
    };

    // Show initial instructions
    calibrationArea.innerHTML = `
        <div class="text-center">
            <h2>Screen Calibration</h2>
            <p>
                This calibration will ensure accurate test results by measuring:
                <br>1. Your viewing distance (should be 40cm)
                <br>2. Your screen's physical size
            </p>
            <button onclick="startCalibration()" class="start-button">Start Calibration</button>
        </div>
    `;

    goBackButton.addEventListener('click', function() {
        if (calibrationInProgress) {
            if (confirm('Are you sure you want to cancel calibration?')) {
                stopCamera();
                window.location.href = 'dashboard';
            }
        } else {
            window.location.href = 'dashboard';
        }
    });
});

async function loadFaceApiModels() {
    if (modelLoaded) return true; // Don't load models if already loaded

    const MODEL_URL = '/static/models';
    
    try {
        console.log('Loading face detection models...');
        
        // Load models one by one with explicit error handling
        await faceapi.nets.tinyFaceDetector.load(MODEL_URL).catch(e => {
            console.error('Error loading tiny face detector:', e);
            throw e;
        });
        console.log('Tiny face detector loaded');
        
        await faceapi.nets.faceLandmark68Net.load(MODEL_URL).catch(e => {
            console.error('Error loading face landmark model:', e);
            throw e;
        });
        console.log('Face landmark model loaded');

        modelLoaded = true;
        console.log('All models loaded successfully');
        return true;
    } catch (error) {
        console.error('Failed to load models:', error);
        return false;
    }
}

async function startCalibration() {
    calibrationInProgress = true;
    const calibrationArea = document.getElementById('calibration-area');

    try {
        // First check if browser supports getUserMedia
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('Your browser does not support camera access');
        }

        // Show loading state
        calibrationArea.innerHTML = `
            <div class="loading-message">
                <h3>Loading face detection models...</h3>
                <p>Please wait...</p>
            </div>
        `;

        // Try to load models
        const modelsLoaded = await loadFaceApiModels();
        if (!modelsLoaded) {
            throw new Error('Failed to load face detection models');
        }

        // Update UI for camera setup
        calibrationArea.innerHTML = `
            <div class="camera-container">
                <video id="video" autoplay playsinline muted></video>
                <div class="distance-indicator">
                    <p>Initializing camera...</p>
                </div>
            </div>
        `;

        // Get video element
        const video = document.getElementById('video');
        if (!video) {
            throw new Error('Failed to create video element');
        }

        // Request camera access
        console.log('Requesting camera access...');
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'user',
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });

        // Attach stream to video element
        video.srcObject = stream;
        console.log('Camera stream attached');

        // Wait for video to be ready
        await new Promise((resolve, reject) => {
            video.onloadedmetadata = resolve;
            video.onerror = () => reject(new Error('Video failed to load'));
            setTimeout(() => reject(new Error('Video loading timeout')), 5000); // 5s timeout
        });

        // Create canvas for face detection visualization
        const canvas = faceapi.createCanvasFromMedia(video);
        canvas.style.position = 'absolute';
        canvas.style.top = '0';
        canvas.style.left = '0';
        video.parentNode.appendChild(canvas);

        // Start face detection loop
        console.log('Starting face detection...');
        startFaceDetection(video, canvas);

    } catch (error) {
        console.error('Calibration error:', error);
        let errorMessage = '';
        let instructions = '';

        switch (error.name) {
            case 'NotAllowedError':
                errorMessage = 'Camera access was denied';
                instructions = 'Please allow camera access in your browser settings and try again.';
                break;
            case 'NotFoundError':
                errorMessage = 'No camera detected';
                instructions = 'Please ensure your device has a working camera and try again.';
                break;
            case 'NotReadableError':
                errorMessage = 'Camera is in use by another application';
                instructions = 'Please close other applications that might be using your camera and try again.';
                break;
            default:
                errorMessage = error.message || 'An unexpected error occurred';
                instructions = 'Please check your camera and browser settings, then try again.';
        }

        calibrationArea.innerHTML = `
            <div class="error-message">
                <h3>Camera Error</h3>
                <p>${errorMessage}</p>
                <p>${instructions}</p>
                <div class="button-group">
                    <button onclick="startCalibration()" class="retry-button">Try Again</button>
                    <button onclick="window.location.href='dashboard'" class="cancel-button">Back to Dashboard</button>
                </div>
            </div>
        `;
    }
}

async function startFaceDetection(video, canvas) {
    const displaySize = { width: video.videoWidth, height: video.videoHeight };
    faceapi.matchDimensions(canvas, displaySize);

    const distanceIndicator = document.querySelector('.distance-indicator');
    let stableDistanceCount = 0;
    let lastDistance = null;

    // Calibration factor (may need adjustment based on testing)
    const CALIBRATION_FACTOR = 25000;

    async function detectFace() {
        if (!calibrationInProgress) return;

        try {
            const detection = await faceapi.detectSingleFace(video, 
                new faceapi.TinyFaceDetectorOptions())
                .withFaceLandmarks();

            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (detection) {
                faceDetected = true;

                // Draw face detection
                const resizedDetection = faceapi.resizeResults(detection, displaySize);
                faceapi.draw.drawDetections(canvas, [resizedDetection]);
                faceapi.draw.drawFaceLandmarks(canvas, [resizedDetection]);

                // Get face dimensions
                const box = detection.detection.box;
                const faceArea = box.width * box.height;
                
                // Calculate distance using face area
                // The larger the face in the frame, the closer the person is
                const estimatedDistance = Math.round(CALIBRATION_FACTOR / faceArea);

                // Update distance value with smoothing
                distance = lastDistance ? 
                    Math.round(0.7 * lastDistance + 0.3 * estimatedDistance) : 
                    estimatedDistance;

                // Debug logs
                console.log('Face Area:', faceArea);
                console.log('Raw Distance:', estimatedDistance);
                console.log('Smoothed Distance:', distance);

                // Update distance indicator
                let message = '';
                let colorClass = '';
                let distanceCm = Math.round(distance / 10);

                if (distanceCm < 30) {
                    message = 'Move back (too close)';
                    colorClass = 'too-close';
                } else if (distanceCm > 40) {
                    message = 'Move closer (too far)';
                    colorClass = 'too-far';
                } else {
                    message = 'Good distance!';
                    colorClass = 'perfect';
                    
                    if (lastDistance && Math.abs(distance - lastDistance) < 20) {
                        stableDistanceCount++;
                        if (stableDistanceCount >= 30) {
                            completeCalibration(distance);
                            return;
                        }
                    } else {
                        stableDistanceCount = 0;
                    }
                }

                lastDistance = distance;

                distanceIndicator.innerHTML = `
                    <p class="${colorClass}">${message}</p>
                    <p>Current distance: ${distanceCm}cm</p>
                    ${colorClass === 'perfect' ? `
                        <div class="progress-bar">
                            <div class="progress" style="width: ${Math.min(100, Math.round(stableDistanceCount/30 * 100))}%"></div>
                        </div>
                        <p>Hold position${'.'.repeat(Math.floor(stableDistanceCount/6))}</p>
                    ` : `<p>Please adjust to 30-40cm from screen</p>`}
                `;

            } else {
                faceDetected = false;
                distanceIndicator.innerHTML = `
                    <p>No face detected</p>
                    <p>Please ensure your face is completely visible and centered</p>
                `;
                stableDistanceCount = 0;
                lastDistance = null;
            }
        } catch (error) {
            console.error('Error in face detection:', error);
        }

        requestAnimationFrame(detectFace);
    }

    detectFace();
}

function completeCalibration(finalDistance) {
    calibrationInProgress = false;
    stopCamera();

    // Calculate and save calibration data
    const calibrationData = {
        scalingFactor: finalDistance / 400, // 400mm is target distance
        targetDistance: 400,
        measuredDistance: finalDistance,
        screenWidth: screenParams.physicalWidth,
        screenHeight: screenParams.physicalHeight,
        pixelDensity: window.devicePixelRatio,
        calibrationDate: new Date().toISOString()
    };

    localStorage.setItem('screenCalibration', JSON.stringify(calibrationData));

    // Show success message and redirect
    const calibrationArea = document.getElementById('calibration-area');
    calibrationArea.innerHTML = `
        <div class="success-message">
            <h2>Calibration Complete!</h2>
            <p>Your screen is now calibrated for accurate testing.</p>
            <p>Redirecting to tests...</p>
        </div>
    `;

    setTimeout(() => {
        window.location.href = '/allTests';
    }, 2000);
}

function stopCamera() {
    const video = document.getElementById('video');
    if (video && video.srcObject) {
        const tracks = video.srcObject.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
    }
}