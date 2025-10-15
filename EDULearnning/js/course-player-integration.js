/**
 * Course Player Integration Module
 * Handles assessment and certificate integration for course player
 * 
 * Usage: Include this script in courser.html after api.js
 * <script type="module" src="js/course-player-integration.js"></script>
 */

import { 
    assessmentAPI, 
    testResultAPI, 
    certificateAPI, 
    courseAPI,
    getAuthToken, 
    getCurrentUserId,
    handleAPIError 
} from './api.js';

// Global state
window.coursePlayerState = {
    currentCourse: null,
    currentAssessments: [],
    currentResults: [],
    currentAssessment: null,
    currentQuestionIndex: 0,
    userAnswers: [],
    timerInterval: null,
    timeRemaining: 0,
    startTime: null
};

// ============================================
// MAIN COURSE LOADING FUNCTIONS
// ============================================

/**
 * Load course with assessments and results
 */
export async function loadCourseWithAssessments(courseId) {
    try {
        const token = getAuthToken();
        const userId = getCurrentUserId();
        
        if (!token || !userId) {
            showToast('Please login to continue', 'error');
            window.location.href = 'login.html';
            return;
        }
        
        // Show loading
        showLoading(true);
        
        // Load course data
        const courseResponse = await courseAPI.getCourseById(courseId);
        const course = await handleAPIError(courseResponse);
        window.coursePlayerState.currentCourse = course;
        
        // Load assessments for this course
        const assessmentsResponse = await assessmentAPI.getCourseAssessments(courseId);
        const assessments = await handleAPIError(assessmentsResponse);
        window.coursePlayerState.currentAssessments = assessments || [];
        
        // Load user's test results
        const resultsResponse = await testResultAPI.getUserCourseResults(userId, courseId, token);
        const results = await handleAPIError(resultsResponse);
        window.coursePlayerState.currentResults = results || [];
        
        // Render course info
        renderCourseInfo(course);
        
        // Render curriculum with assessments
        renderCourseCurriculum(course, assessments, results);
        
        // Check certificate eligibility
        await checkAndDisplayCertificate(courseId);
        
        showLoading(false);
        
    } catch (error) {
        console.error('Error loading course:', error);
        showToast('Failed to load course: ' + error.message, 'error');
        showLoading(false);
    }
}

/**
 * Render course information in header
 */
function renderCourseInfo(course) {
    document.getElementById('courseTitle').textContent = course.title || 'Course';
    document.getElementById('instructorName').textContent = course.instructor || 'Instructor';
    
    // Set instructor initials
    const initials = (course.instructor || 'IN').split(' ').map(n => n[0]).join('').toUpperCase();
    document.getElementById('instructorInitials').textContent = initials;
}

/**
 * Render course curriculum with lessons and assessments
 */
function renderCourseCurriculum(course, assessments, results) {
    const contentDiv = document.getElementById('courseContent');
    let html = '';
    
    let totalItems = 0;
    let completedItems = 0;
    
    // Iterate through modules
    course.modules.forEach((module, moduleIndex) => {
        const moduleAssessments = assessments.filter(a => a.moduleId === module.id);
        
        // Check if all lessons in module are completed
        const completedLessons = module.lessons.filter(l => l.completed).length;
        const totalLessons = module.lessons.length;
        const allLessonsCompleted = completedLessons === totalLessons;
        
        totalItems += totalLessons;
        completedItems += completedLessons;
        
        // Module header
        html += `
            <div class="module">
                <div class="module-header" onclick="toggleModule(this)">
                    <div class="module-title">${module.title}</div>
                    <div class="module-progress">${completedLessons}/${totalLessons} lessons</div>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="module-content">
        `;
        
        // Render lessons
        module.lessons.forEach((lesson, lessonIndex) => {
            html += `
                <div class="lesson ${lesson.completed ? 'completed' : ''} ${lesson.active ? 'active' : ''}" 
                     onclick="playLesson('${lesson.id}', '${module.id}', '${course._id}')">
                    <div class="lesson-icon">
                        <i class="fas ${lesson.completed ? 'fa-check-circle' : lesson.active ? 'fa-play-circle' : 'fa-circle'}"></i>
                    </div>
                    <div class="lesson-title">${lesson.title}</div>
                    <div class="lesson-duration">${lesson.duration || ''}</div>
                </div>
            `;
        });
        
        // Render assessments for this module
        moduleAssessments.forEach(assessment => {
            const assessmentResult = results.find(r => r.assessmentId === assessment._id);
            const passed = assessmentResult?.passed || false;
            const score = assessmentResult?.score || 0;
            const locked = !allLessonsCompleted;
            
            totalItems++;
            if (passed) completedItems++;
            
            const assessmentType = assessment.type === 'mcq' ? 'Quiz' : 'Assignment';
            const assessmentIcon = assessment.type === 'mcq' ? 'fa-clipboard-list' : 'fa-file-alt';
            
            html += `
                <div class="assessment-item ${locked ? 'locked' : ''} ${passed ? 'passed' : ''}" 
                     onclick="${locked ? '' : `startAssessment('${assessment._id}', '${assessment.type}')`}">
                    <div class="assessment-icon">
                        <i class="fas ${passed ? 'fa-check-circle' : locked ? 'fa-lock' : assessmentIcon}"></i>
                    </div>
                    <div class="assessment-title">
                        ${assessment.title}
                        ${locked ? '<br><small style="color: var(--gray); font-weight: normal;">🔒 Complete all lessons to unlock</small>' : ''}
                    </div>
                    <div class="assessment-badge">${assessmentType}</div>
                    ${passed ? `<div class="assessment-score">✓ ${score}%</div>` : ''}
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    });
    
    // Add certificate notice
    const allCompleted = completedItems === totalItems && totalItems > 0;
    html += `
        <div class="certificate-notice">
            <h4><i class="fas fa-certificate"></i> ${allCompleted ? 'Certificate Available!' : 'Certificate of Completion'}</h4>
            <p>${allCompleted ? 
                'Congratulations! You have completed all requirements and earned your certificate.' : 
                'Complete all lessons and pass all assessments to earn your certificate.'
            }</p>
            <button class="certificate-button" id="generateCertBtn" style="display: ${allCompleted ? 'inline-flex' : 'none'};" 
                    onclick="generateCourseCertificate('${course._id}')">
                <i class="fas fa-award"></i> Generate Certificate
            </button>
        </div>
    `;
    
    contentDiv.innerHTML = html;
    
    // Update progress
    updateProgress(completedItems, totalItems);
}

/**
 * Update progress bar and text
 */
function updateProgress(completed, total) {
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
    document.getElementById('progressFill').style.width = `${percentage}%`;
    document.getElementById('progressText').innerHTML = `
        <span>${percentage}% completed</span>
        <span>${completed}/${total} items</span>
    `;
}

/**
 * Toggle module expand/collapse
 */
window.toggleModule = function(headerElement) {
    headerElement.classList.toggle('collapsed');
    const content = headerElement.nextElementSibling;
    content.classList.toggle('collapsed');
};

/**
 * Play a lesson
 */
window.playLesson = function(lessonId, moduleId, courseId) {
    const course = window.coursePlayerState.currentCourse;
    if (!course) return;
    
    // Find the lesson
    let foundLesson = null;
    let foundModule = null;
    
    for (const module of course.modules) {
        if (module.id === moduleId) {
            foundModule = module;
            foundLesson = module.lessons.find(l => l.id === lessonId);
            if (foundLesson) break;
        }
    }
    
    if (!foundLesson) return;
    
    // Update video player
    const videoPlayer = document.getElementById('videoPlayer');
    if (foundLesson.videoUrl) {
        videoPlayer.src = foundLesson.videoUrl;
    }
    
    // Mark as active
    document.querySelectorAll('.lesson').forEach(l => l.classList.remove('active'));
    event.target.closest('.lesson').classList.add('active');
    
    // Mark as completed if not already
    if (!foundLesson.completed) {
        foundLesson.completed = true;
        event.target.closest('.lesson').classList.add('completed');
        
        // Re-render to update progress and unlock assessments
        const { currentAssessments, currentResults } = window.coursePlayerState;
        renderCourseCurriculum(course, currentAssessments, currentResults);
    }
};

// ============================================
// ASSESSMENT FUNCTIONS
// ============================================

/**
 * Start an assessment (MCQ or Assignment)
 */
window.startAssessment = async function(assessmentId, type) {
    try {
        const token = getAuthToken();
        
        // Fetch assessment details
        const response = await assessmentAPI.getAssessment(assessmentId);
        const assessment = await handleAPIError(response);
        
        window.coursePlayerState.currentAssessment = assessment;
        window.coursePlayerState.currentQuestionIndex = 0;
        window.coursePlayerState.userAnswers = [];
        window.coursePlayerState.startTime = Date.now();
        
        if (type === 'mcq') {
            showMCQModal(assessment);
        } else {
            showAssignmentModal(assessment);
        }
        
    } catch (error) {
        console.error('Error starting assessment:', error);
        showToast('Failed to load assessment: ' + error.message, 'error');
    }
};

/**
 * Show MCQ modal
 */
function showMCQModal(assessment) {
    const modal = document.getElementById('mcqModal');
    document.getElementById('mcqTitle').textContent = assessment.title;
    
    // Initialize answers array
    window.coursePlayerState.userAnswers = new Array(assessment.questions.length).fill(null);
    
    // Show timer if time limit exists
    if (assessment.timeLimit) {
        document.getElementById('mcqTimer').style.display = 'flex';
        startTimer(assessment.timeLimit);
    } else {
        document.getElementById('mcqTimer').style.display = 'none';
    }
    
    // Render first question
    renderQuestion(0);
    
    // Show modal
    modal.style.display = 'flex';
}

/**
 * Render a question
 */
function renderQuestion(index) {
    const assessment = window.coursePlayerState.currentAssessment;
    const question = assessment.questions[index];
    const userAnswer = window.coursePlayerState.userAnswers[index];
    
    const bodyDiv = document.getElementById('mcqBody');
    
    let html = `
        <div class="question-container">
            <div class="question-header">
                <div class="question-number">Question ${index + 1} of ${assessment.questions.length}</div>
            </div>
            <div class="question-text">${question.text}</div>
            <div class="options-container">
    `;
    
    question.options.forEach((option, optionIndex) => {
        const isSelected = userAnswer === optionIndex;
        html += `
            <div class="option ${isSelected ? 'selected' : ''}" onclick="selectOption(${index}, ${optionIndex})">
                <div class="option-radio"></div>
                <span>${option}</span>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    bodyDiv.innerHTML = html;
    
    // Update progress bar
    const progress = ((index + 1) / assessment.questions.length) * 100;
    document.getElementById('mcqProgressFill').style.width = `${progress}%`;
    
    // Update question indicator
    document.getElementById('questionIndicator').textContent = `Question ${index + 1} of ${assessment.questions.length}`;
    
    // Update navigation buttons
    document.getElementById('prevQuestion').disabled = index === 0;
    
    const nextBtn = document.getElementById('nextQuestion');
    if (index === assessment.questions.length - 1) {
        nextBtn.textContent = 'Submit Test';
        nextBtn.onclick = submitMCQTest;
    } else {
        nextBtn.innerHTML = 'Next <i class="fas fa-arrow-right"></i>';
        nextBtn.onclick = nextQuestion;
    }
    
    window.coursePlayerState.currentQuestionIndex = index;
}

/**
 * Select an option
 */
window.selectOption = function(questionIndex, optionIndex) {
    window.coursePlayerState.userAnswers[questionIndex] = optionIndex;
    renderQuestion(questionIndex);
};

/**
 * Previous question
 */
window.previousQuestion = function() {
    const currentIndex = window.coursePlayerState.currentQuestionIndex;
    if (currentIndex > 0) {
        renderQuestion(currentIndex - 1);
    }
};

/**
 * Next question
 */
window.nextQuestion = function() {
    const assessment = window.coursePlayerState.currentAssessment;
    const currentIndex = window.coursePlayerState.currentQuestionIndex;
    
    if (currentIndex < assessment.questions.length - 1) {
        renderQuestion(currentIndex + 1);
    }
};

/**
 * Submit MCQ test
 */
window.submitMCQTest = async function() {
    try {
        const { currentAssessment, userAnswers, startTime } = window.coursePlayerState;
        
        // Check if all questions answered
        const unanswered = userAnswers.filter(a => a === null).length;
        if (unanswered > 0) {
            if (!confirm(`You have ${unanswered} unanswered question(s). Submit anyway?`)) {
                return;
            }
        }
        
        // Stop timer
        stopTimer();
        
        // Calculate time spent (in minutes)
        const timeSpent = Math.round((Date.now() - startTime) / 60000);
        
        // Prepare answers
        const answers = currentAssessment.questions.map((q, index) => ({
            questionId: q.id,
            answer: userAnswers[index]
        }));
        
        // Show loading
        const nextBtn = document.getElementById('nextQuestion');
        nextBtn.disabled = true;
        nextBtn.innerHTML = '<span class="loading-spinner"></span> Submitting...';
        
        // Submit to backend
        const token = getAuthToken();
        const response = await testResultAPI.submitTest({
            assessmentId: currentAssessment._id,
            answers: answers,
            timeSpent: timeSpent
        }, token);
        
        const result = await handleAPIError(response);
        
        // Show results
        showTestResults(result);
        
    } catch (error) {
        console.error('Error submitting test:', error);
        showToast('Failed to submit test: ' + error.message, 'error');
        document.getElementById('nextQuestion').disabled = false;
        document.getElementById('nextQuestion').textContent = 'Submit Test';
    }
};

/**
 * Show test results
 */
function showTestResults(result) {
    const bodyDiv = document.getElementById('mcqBody');
    const passed = result.passed;
    const score = result.score;
    const assessment = window.coursePlayerState.currentAssessment;
    
    const correctAnswers = result.answers.filter(a => a.correct).length;
    const totalQuestions = result.answers.length;
    
    bodyDiv.innerHTML = `
        <div class="results-container">
            <div class="results-icon ${passed ? 'pass' : 'fail'}">
                <i class="fas ${passed ? 'fa-check-circle' : 'fa-times-circle'}"></i>
            </div>
            <h2 class="results-title">${passed ? 'Congratulations!' : 'Keep Trying!'}</h2>
            <div class="results-score">${score}%</div>
            <p class="results-message">
                ${passed ? 
                    'You passed the assessment! The next module is now unlocked.' : 
                    `You need ${assessment.passingScore}% to pass. You can try again.`
                }
            </p>
            <div class="results-details">
                <div class="result-stat">
                    <div class="result-stat-value">${correctAnswers}</div>
                    <div class="result-stat-label">Correct Answers</div>
                </div>
                <div class="result-stat">
                    <div class="result-stat-value">${totalQuestions}</div>
                    <div class="result-stat-label">Total Questions</div>
                </div>
                <div class="result-stat">
                    <div class="result-stat-value">${result.timeSpent} min</div>
                    <div class="result-stat-label">Time Spent</div>
                </div>
            </div>
            <button class="mcq-button primary" onclick="closeMCQModal(${passed})">
                ${passed ? 'Continue' : 'Close'}
            </button>
        </div>
    `;
    
    // Hide navigation
    document.getElementById('mcqProgressFill').style.width = '100%';
    document.querySelector('.mcq-navigation').style.display = 'none';
}

/**
 * Close MCQ modal
 */
window.closeMCQModal = function(passed) {
    document.getElementById('mcqModal').style.display = 'none';
    stopTimer();
    
    if (passed) {
        // Reload course to update progress
        const courseId = window.coursePlayerState.currentCourse._id;
        loadCourseWithAssessments(courseId);
        showToast('Assessment passed! Next module unlocked.', 'success');
    }
};

/**
 * Start timer
 */
function startTimer(timeLimit) {
    window.coursePlayerState.timeRemaining = timeLimit * 60; // Convert to seconds
    
    updateTimerDisplay();
    
    window.coursePlayerState.timerInterval = setInterval(() => {
        window.coursePlayerState.timeRemaining--;
        updateTimerDisplay();
        
        if (window.coursePlayerState.timeRemaining <= 0) {
            stopTimer();
            alert('Time is up! Submitting your test...');
            submitMCQTest();
        }
    }, 1000);
}

/**
 * Stop timer
 */
function stopTimer() {
    if (window.coursePlayerState.timerInterval) {
        clearInterval(window.coursePlayerState.timerInterval);
        window.coursePlayerState.timerInterval = null;
    }
}

/**
 * Update timer display
 */
function updateTimerDisplay() {
    const seconds = window.coursePlayerState.timeRemaining;
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    document.getElementById('timerDisplay').textContent = 
        `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// ============================================
// ASSIGNMENT FUNCTIONS
// ============================================

/**
 * Show assignment modal
 */
function showAssignmentModal(assessment) {
    const modal = document.getElementById('assignmentModal');
    document.getElementById('assignmentTitle').textContent = assessment.title;
    document.getElementById('assignmentInstructions').innerHTML = `
        <h4><i class="fas fa-info-circle"></i> Instructions</h4>
        <p>${assessment.instructions || 'Complete the assignment and submit your answer below.'}</p>
    `;
    document.getElementById('assignmentText').value = '';
    
    modal.style.display = 'flex';
}

/**
 * Close assignment modal
 */
window.closeAssignmentModal = function() {
    document.getElementById('assignmentModal').style.display = 'none';
};

/**
 * Submit assignment
 */
window.submitAssignment = async function() {
    try {
        const assessment = window.coursePlayerState.currentAssessment;
        const answerText = document.getElementById('assignmentText').value.trim();
        
        if (!answerText) {
            showToast('Please write your answer before submitting', 'error');
            return;
        }
        
        // Show loading
        const submitBtn = document.querySelector('#assignmentModal .modal-button.primary');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading-spinner"></span> Submitting...';
        
        // Calculate time spent
        const timeSpent = Math.round((Date.now() - window.coursePlayerState.startTime) / 60000);
        
        // Submit to backend
        const token = getAuthToken();
        const response = await testResultAPI.submitTest({
            assessmentId: assessment._id,
            answers: [{ questionId: 'assignment', answer: answerText }],
            timeSpent: timeSpent
        }, token);
        
        const result = await handleAPIError(response);
        
        // Close modal
        closeAssignmentModal();
        
        // Show success message
        showToast('Assignment submitted successfully! Waiting for instructor to grade.', 'success');
        
        // Reload course
        const courseId = window.coursePlayerState.currentCourse._id;
        loadCourseWithAssessments(courseId);
        
    } catch (error) {
        console.error('Error submitting assignment:', error);
        showToast('Failed to submit assignment: ' + error.message, 'error');
        document.querySelector('#assignmentModal .modal-button.primary').disabled = false;
        document.querySelector('#assignmentModal .modal-button.primary').innerHTML = 'Submit Assignment';
    }
};

// ============================================
// CERTIFICATE FUNCTIONS
// ============================================

/**
 * Check and display certificate eligibility
 */
async function checkAndDisplayCertificate(courseId) {
    try {
        const token = getAuthToken();
        const response = await certificateAPI.checkEligibility(courseId, token);
        const eligibility = await handleAPIError(response);
        
        if (eligibility.eligible) {
            const btn = document.getElementById('generateCertBtn');
            if (btn) {
                btn.style.display = 'inline-flex';
            }
        }
    } catch (error) {
        console.error('Error checking certificate eligibility:', error);
    }
}

/**
 * Generate course certificate
 */
window.generateCourseCertificate = async function(courseId) {
    try {
        const token = getAuthToken();
        
        // Show loading
        const btn = document.getElementById('generateCertBtn');
        btn.disabled = true;
        btn.innerHTML = '<span class="loading-spinner"></span> Generating...';
        
        // Generate certificate
        const response = await certificateAPI.generateCertificate(courseId, token);
        const certificate = await handleAPIError(response);
        
        showToast('Certificate generated successfully!', 'success');
        
        // Download PDF
        const pdfResponse = await certificateAPI.downloadCertificatePDF(certificate._id, token);
        const blob = await pdfResponse.blob();
        
        // Trigger download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `certificate_${certificate.certificateId}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // Reset button
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-award"></i> Generate Certificate';
        
    } catch (error) {
        console.error('Error generating certificate:', error);
        showToast('Failed to generate certificate: ' + error.message, 'error');
        const btn = document.getElementById('generateCertBtn');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-award"></i> Generate Certificate';
    }
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const icon = document.getElementById('toastIcon');
    const messageSpan = document.getElementById('toastMessage');
    
    // Set message
    messageSpan.textContent = message;
    
    // Set icon and style
    toast.className = `toast ${type}`;
    if (type === 'success') {
        icon.className = 'fas fa-check-circle';
    } else {
        icon.className = 'fas fa-exclamation-circle';
    }
    
    // Show toast
    toast.classList.add('show');
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/**
 * Show/hide loading indicator
 */
function showLoading(show) {
    const contentDiv = document.getElementById('courseContent');
    if (show) {
        contentDiv.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--gray);">
                <i class="fas fa-spinner fa-spin" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                <p>Loading course content...</p>
            </div>
        `;
    }
}

// ============================================
// INITIALIZE ON PAGE LOAD
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    const token = getAuthToken();
    if (!token) {
        showToast('Please login to access this course', 'error');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
        return;
    }
    
    // Get course ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const courseId = urlParams.get('id');
    
    if (!courseId) {
        showToast('No course ID provided', 'error');
        return;
    }
    
    // Load course with assessments
    await loadCourseWithAssessments(courseId);
});

// Export main function for external use
window.loadCourseWithAssessments = loadCourseWithAssessments;
