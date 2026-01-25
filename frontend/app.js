/**
 * AI Interview Agent - Frontend Application
 * Modern ES6+ JavaScript with async/await and modular architecture
 */

// ============================================
// Configuration
// ============================================
const CONFIG = {
    API_BASE: 'http://localhost:8000',
    EDGE_TTS_VOICE: 'en-US-AriaNeural', // Microsoft Edge TTS voice
    SPEECH_LANG: 'en-US'
};

// ============================================
// Application State
// ============================================
const AppState = {
    threadId: sessionStorage.getItem('interview_thread_id') || null,
    currentSection: 'hero',
    resumeFile: null,
    jdFile: null,
    isRecording: false,
    isSpeaking: false,
    questionCount: 0,
    topics: [],
    currentTopic: ''
};

// ============================================
// Utility Functions
// ============================================
const Utils = {
    /**
     * Save thread ID to session storage
     */
    saveThreadId(threadId) {
        AppState.threadId = threadId;
        sessionStorage.setItem('interview_thread_id', threadId);
    },

    /**
     * Clear session data
     */
    clearSession() {
        AppState.threadId = null;
        sessionStorage.removeItem('interview_thread_id');
    },

    /**
     * Sleep utility for async operations
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    /**
     * Extract clean question text from backend response
     * Handles cases where question might be an object or contain metadata
     */
    extractQuestionText(question) {
        if (!question) return '';

        // If it's a string, clean it up
        if (typeof question === 'string') {
            // Remove any JSON-like metadata that might be embedded
            let cleanText = question;

            // Try to extract just the question if it contains metadata patterns
            // Pattern: Remove things like "status: ongoing," or "question_count: 2"
            cleanText = cleanText.replace(/\b(status|question_count|topic_index|current_topic_index)\s*[:=]\s*[\w\d]+[,;]?\s*/gi, '');

            // Remove any leading/trailing quotes or braces
            cleanText = cleanText.replace(/^[{"'\s]+|[}"'\s]+$/g, '');

            // If it looks like "question: actual question", extract the question part
            const questionMatch = cleanText.match(/(?:question|text)\s*[:=]\s*["']?(.+?)["']?$/i);
            if (questionMatch) {
                cleanText = questionMatch[1];
            }

            return cleanText.trim();
        }

        // If it's an object, try to extract the question field
        if (typeof question === 'object') {
            return question.question || question.text || question.content || String(question);
        }

        return String(question);
    }
};

// ============================================
// Toast Notification System
// ============================================
const Toast = {
    container: null,

    init() {
        this.container = document.getElementById('toast-container');
    },

    show(message, type = 'info', duration = 4000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icons = {
            success: '✓',
            error: '✕',
            info: 'ℹ',
            warning: '⚠'
        };

        toast.innerHTML = `
            <span class="text-lg">${icons[type] || icons.info}</span>
            <span>${message}</span>
        `;

        this.container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    success(message) { this.show(message, 'success'); },
    error(message) { this.show(message, 'error'); },
    info(message) { this.show(message, 'info'); },
    warning(message) { this.show(message, 'warning'); }
};

// ============================================
// UI Controller
// ============================================
const UI = {
    sections: ['hero', 'upload', 'interview', 'enhancer', 'results'],

    /**
     * Show a specific section and hide all others
     */
    showSection(sectionName) {
        this.sections.forEach(name => {
            const section = document.getElementById(`${name}-section`);
            if (section) {
                if (name === sectionName) {
                    section.classList.remove('hidden');
                    section.classList.add('section-entering');
                    setTimeout(() => section.classList.remove('section-entering'), 600);
                } else {
                    section.classList.add('hidden');
                }
            }
        });
        AppState.currentSection = sectionName;
    },

    /**
     * Update button loading state
     */
    setButtonLoading(button, isLoading, originalText = null) {
        if (isLoading) {
            button.dataset.originalText = button.textContent;
            button.disabled = true;
            button.innerHTML = `
                <span class="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
                Processing...
            `;
        } else {
            button.disabled = false;
            button.textContent = originalText || button.dataset.originalText;
        }
    },

    /**
     * Update question display
     */
    updateQuestion(questionText) {
        const display = document.getElementById('question-display');
        display.innerHTML = `<p class="text-2xl md:text-3xl font-light leading-relaxed text-gray-200">${questionText}</p>`;
    },

    /**
     * Update topic display
     */
    updateTopic(topic) {
        document.getElementById('current-topic').textContent = `Topic: ${topic}`;
        AppState.currentTopic = topic;
    },

    /**
     * Update question counter
     */
    updateQuestionCounter(count) {
        document.getElementById('question-counter').textContent = `Q ${count}`;
        AppState.questionCount = count;
    },

    /**
     * Display results from final evaluation
     */
    displayResults(result) {
        // Final Score
        document.getElementById('final-score').textContent = `${result.final_score}/5`;

        // Recommendation
        const recText = document.getElementById('recommendation-text');
        const recBadge = document.getElementById('recommendation-badge');
        recText.textContent = result.recommendation.toUpperCase();

        // Style based on recommendation
        if (result.recommendation.toLowerCase() === 'hire') {
            recBadge.className = 'px-8 py-4 rounded-xl bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30';
            recText.className = 'text-2xl font-bold text-green-400';
        } else if (result.recommendation.toLowerCase() === 'maybe') {
            recBadge.className = 'px-8 py-4 rounded-xl bg-gradient-to-r from-amber-500/20 to-yellow-500/20 border border-amber-500/30';
            recText.className = 'text-2xl font-bold text-amber-400';
        } else {
            recBadge.className = 'px-8 py-4 rounded-xl bg-gradient-to-r from-red-500/20 to-rose-500/20 border border-red-500/30';
            recText.className = 'text-2xl font-bold text-red-400';
        }

        // Strengths
        const strengthsList = document.getElementById('strengths-list');
        strengthsList.innerHTML = result.strengths.map(s => `
            <li class="flex items-start gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-green-400 mt-2 flex-shrink-0"></span>
                <span>${s}</span>
            </li>
        `).join('');

        // Weaknesses
        const weaknessesList = document.getElementById('weaknesses-list');
        weaknessesList.innerHTML = result.weaknesses.map(w => `
            <li class="flex items-start gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400 mt-2 flex-shrink-0"></span>
                <span>${w}</span>
            </li>
        `).join('');

        // Topic Scores
        const topicScoresContainer = document.getElementById('topic-scores');
        topicScoresContainer.innerHTML = Object.entries(result.topic_scores).map(([topic, score]) => `
            <div class="space-y-2">
                <div class="flex justify-between text-sm">
                    <span class="text-gray-300">${topic}</span>
                    <span class="text-accent-secondary">${score}/5</span>
                </div>
                <div class="topic-bar">
                    <div class="topic-bar-fill" style="width: ${(score / 5) * 100}%"></div>
                </div>
            </div>
        `).join('');

        // Summary
        document.getElementById('result-summary').textContent = result.summary;
    }
};

// ============================================
// API Service
// ============================================
const API = {
    /**
     * Start interview - upload resume and JD
     */
    async startInterview(resumeFile, jdFile) {
        const formData = new FormData();
        formData.append('resume', resumeFile);
        formData.append('jd', jdFile);

        const response = await fetch(`${CONFIG.API_BASE}/start-interview`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to start interview');
        }

        return response.json();
    },

    /**
     * Proceed to interview after screening
     */
    async proceedToInterview(threadId) {
        const response = await fetch(`${CONFIG.API_BASE}/proceed-to-interview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ thread_id: threadId })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to proceed to interview');
        }

        return response.json();
    },

    /**
     * Submit an answer and get next question
     */
    async submitAnswer(threadId, answer) {
        const response = await fetch(`${CONFIG.API_BASE}/submit-answer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ thread_id: threadId, answer })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to submit answer');
        }

        return response.json();
    },

    /**
     * Get enhanced resume content
     */
    async getEnhancedResume() {
        const response = await fetch(`${CONFIG.API_BASE}/get-enhanced-resume`, {
            method: 'GET'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get enhanced resume');
        }

        return response.json();
    }
};

// ============================================
// File Upload Handler
// ============================================
const FileUpload = {
    init() {
        this.setupDropzone('resume-dropzone', 'resume-input', 'resume-filename', 'resumeFile');
        this.setupDropzone('jd-dropzone', 'jd-input', 'jd-filename', 'jdFile');
    },

    setupDropzone(dropzoneId, inputId, filenameId, stateKey) {
        const dropzone = document.getElementById(dropzoneId);
        const input = document.getElementById(inputId);
        const filenameDisplay = document.getElementById(filenameId);

        // Drag events
        ['dragenter', 'dragover'].forEach(event => {
            dropzone.addEventListener(event, (e) => {
                e.preventDefault();
                dropzone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(event => {
            dropzone.addEventListener(event, (e) => {
                e.preventDefault();
                dropzone.classList.remove('drag-over');
            });
        });

        // Drop handler
        dropzone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFile(files[0], dropzone, filenameDisplay, stateKey);
            }
        });

        // Click handler
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFile(e.target.files[0], dropzone, filenameDisplay, stateKey);
            }
        });
    },

    handleFile(file, dropzone, filenameDisplay, stateKey) {
        // Validate file type
        const validTypes = ['application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];

        if (!validTypes.includes(file.type) && !file.name.endsWith('.pdf')) {
            Toast.error('Please upload a PDF or Word document');
            return;
        }

        // Update state
        AppState[stateKey] = file;

        // Update UI
        dropzone.classList.add('file-selected');
        filenameDisplay.textContent = file.name;

        // Check if both files are ready
        this.checkReadyState();
    },

    checkReadyState() {
        const submitBtn = document.getElementById('btn-submit-docs');
        if (AppState.resumeFile && AppState.jdFile) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }
};

// ============================================
// Voice UI - Waveform Visualizer
// ============================================
const VoiceUI = {
    container: null,

    init() {
        this.container = document.getElementById('waveform-container');
    },

    startAnimation() {
        this.container.classList.add('waveform-active');
    },

    stopAnimation() {
        this.container.classList.remove('waveform-active');
    }
};

// ============================================
// Text-to-Speech (Edge-TTS via Web Speech API)
// ============================================
const TTS = {
    synth: window.speechSynthesis,
    voice: null,

    init() {
        // Wait for voices to load
        if (this.synth.onvoiceschanged !== undefined) {
            this.synth.onvoiceschanged = () => this.loadVoice();
        }
        this.loadVoice();
    },

    loadVoice() {
        const voices = this.synth.getVoices();
        // Try to find a Microsoft Edge voice or any en-US voice
        this.voice = voices.find(v => v.name.includes('Microsoft') && v.lang.startsWith('en')) ||
            voices.find(v => v.lang.startsWith('en-US')) ||
            voices.find(v => v.lang.startsWith('en')) ||
            voices[0];
    },

    async speak(text) {
        return new Promise((resolve) => {
            // Cancel any ongoing speech
            this.synth.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.voice = this.voice;
            utterance.rate = 0.95;
            utterance.pitch = 1;
            utterance.volume = 1;

            utterance.onstart = () => {
                AppState.isSpeaking = true;
                VoiceUI.startAnimation();
            };

            utterance.onend = () => {
                AppState.isSpeaking = false;
                VoiceUI.stopAnimation();
                resolve();
            };

            utterance.onerror = () => {
                AppState.isSpeaking = false;
                VoiceUI.stopAnimation();
                resolve();
            };

            this.synth.speak(utterance);
        });
    },

    stop() {
        this.synth.cancel();
        AppState.isSpeaking = false;
        VoiceUI.stopAnimation();
    }
};

// ============================================
// Speech Recognition (Web Speech API)
// ============================================
const SpeechRecognition = {
    recognition: null,
    isSupported: false,
    transcript: '',

    init() {
        const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognitionAPI) {
            console.warn('Speech Recognition not supported');
            Toast.warning('Voice input not supported in this browser. Please type your answers.');
            return;
        }

        this.isSupported = true;
        this.recognition = new SpeechRecognitionAPI();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = CONFIG.SPEECH_LANG;

        this.recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const result = event.results[i];
                if (result.isFinal) {
                    finalTranscript += result[0].transcript + ' ';
                } else {
                    interimTranscript += result[0].transcript;
                }
            }

            this.transcript = this.transcript + finalTranscript;
            const displayText = this.transcript + interimTranscript;

            document.getElementById('user-transcript').textContent = displayText || 'Listening...';
            document.getElementById('answer-input').value = displayText;
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            if (event.error === 'not-allowed') {
                Toast.error('Microphone access denied. Please allow microphone access.');
            }
            this.stop();
        };

        this.recognition.onend = () => {
            if (AppState.isRecording) {
                // Restart if still supposed to be recording
                try {
                    this.recognition.start();
                } catch (e) {
                    console.warn('Could not restart recognition:', e);
                }
            }
        };
    },

    start() {
        if (!this.isSupported) {
            Toast.warning('Voice input not supported');
            return;
        }

        this.transcript = '';
        AppState.isRecording = true;

        try {
            this.recognition.start();
            document.getElementById('mic-indicator').classList.add('recording');
            document.getElementById('mic-text').textContent = 'Stop Recording';
            document.getElementById('btn-mic').classList.add('bg-red-500/20');
            VoiceUI.startAnimation();
        } catch (e) {
            console.error('Could not start recognition:', e);
        }
    },

    stop() {
        AppState.isRecording = false;

        if (this.recognition) {
            try {
                this.recognition.stop();
            } catch (e) {
                console.warn('Recognition already stopped');
            }
        }

        document.getElementById('mic-indicator').classList.remove('recording');
        document.getElementById('mic-text').textContent = 'Start Recording';
        document.getElementById('btn-mic').classList.remove('bg-red-500/20');
        VoiceUI.stopAnimation();
    },

    toggle() {
        if (AppState.isRecording) {
            this.stop();
        } else {
            this.start();
        }
    }
};

// ============================================
// Main Interview Application
// ============================================
const InterviewApp = {
    init() {
        // Initialize modules
        Toast.init();
        FileUpload.init();
        VoiceUI.init();
        TTS.init();
        SpeechRecognition.init();

        // Bind event handlers
        this.bindEvents();

        // Check for existing session
        if (AppState.threadId) {
            Toast.info('Resuming previous session...');
        }
    },

    bindEvents() {
        // Hero section - Launch button
        document.getElementById('btn-launch').addEventListener('click', () => {
            UI.showSection('upload');
        });

        // Upload section - Submit button
        document.getElementById('btn-submit-docs').addEventListener('click', () => {
            this.handleDocumentUpload();
        });

        // Interview section - Mic button
        document.getElementById('btn-mic').addEventListener('click', () => {
            SpeechRecognition.toggle();
        });

        // Interview section - Submit answer
        document.getElementById('btn-submit-answer').addEventListener('click', () => {
            this.handleAnswerSubmit();
        });

        // Interview section - Replay question
        document.getElementById('btn-replay-question').addEventListener('click', () => {
            const questionText = document.getElementById('question-display').textContent;
            TTS.speak(questionText);
        });

        // Interview section - End interview
        document.getElementById('btn-end-interview').addEventListener('click', () => {
            this.handleEndInterview();
        });

        // Enhancer section - Try again
        document.getElementById('btn-try-again').addEventListener('click', () => {
            Utils.clearSession();
            UI.showSection('upload');
            this.resetUploadForm();
        });

        // Results section - New interview
        document.getElementById('btn-new-interview').addEventListener('click', () => {
            Utils.clearSession();
            UI.showSection('hero');
            this.resetUploadForm();
        });

        // Results section - Download report
        document.getElementById('btn-download-report').addEventListener('click', () => {
            Toast.info('Report download feature coming soon!');
        });

        // Enhancer section - Download enhanced resume
        document.getElementById('btn-download-enhanced').addEventListener('click', () => {
            this.downloadEnhancedResume();
        });
    },

    async handleDocumentUpload() {
        const submitBtn = document.getElementById('btn-submit-docs');
        const loadingEl = document.getElementById('upload-loading');

        try {
            UI.setButtonLoading(submitBtn, true);
            loadingEl.classList.remove('hidden');

            // Call API
            const result = await API.startInterview(AppState.resumeFile, AppState.jdFile);

            // Save thread ID
            Utils.saveThreadId(result.thread_id);

            Toast.success(`Resume analyzed! Score: ${(result.resume_score * 100).toFixed(0)}%`);

            // Route based on score
            if (result.can_proceed) {
                // Proceed to interview
                await this.proceedToInterview();
            } else {
                // Show enhancer
                document.getElementById('enhancer-score').textContent =
                    `${(result.resume_score * 100).toFixed(0)}%`;
                UI.showSection('enhancer');
                // Load enhanced resume content
                await this.loadEnhancedResume();
            }

        } catch (error) {
            console.error('Upload error:', error);
            Toast.error(error.message || 'Failed to process documents');
        } finally {
            UI.setButtonLoading(submitBtn, false, 'Start Screening');
            loadingEl.classList.add('hidden');
        }
    },

    async proceedToInterview() {
        try {
            const result = await API.proceedToInterview(AppState.threadId);

            if (result.status === 'failed_screening') {
                UI.showSection('enhancer');
                await this.loadEnhancedResume();
                return;
            }

            // Store topics
            AppState.topics = result.topics || [];

            // Show interview section
            UI.showSection('interview');

            // Extract clean question text
            const questionText = Utils.extractQuestionText(result.first_question);

            // Update UI with clean question
            UI.updateQuestion(questionText);
            UI.updateTopic(AppState.topics[0] || 'General');
            UI.updateQuestionCounter(1);

            // Speak only the clean question
            await Utils.sleep(500);
            await TTS.speak(questionText);

        } catch (error) {
            console.error('Proceed error:', error);
            Toast.error(error.message || 'Failed to start interview');
        }
    },

    async handleAnswerSubmit() {
        const answerInput = document.getElementById('answer-input');
        const answer = answerInput.value.trim();

        if (!answer) {
            Toast.warning('Please provide an answer before submitting');
            return;
        }

        // Stop recording if active
        SpeechRecognition.stop();

        const submitBtn = document.getElementById('btn-submit-answer');

        try {
            UI.setButtonLoading(submitBtn, true);

            const result = await API.submitAnswer(AppState.threadId, answer);

            // Clear input
            answerInput.value = '';
            document.getElementById('user-transcript').textContent =
                'Click the microphone to start speaking, or type your answer below...';
            SpeechRecognition.transcript = '';

            if (result.status === 'completed') {
                // Interview finished - show results
                UI.displayResults(result.final_result);
                UI.showSection('results');
                Toast.success('Interview completed!');
                Utils.clearSession();
            } else {
                // Extract clean question text
                const questionText = Utils.extractQuestionText(result.next_question);

                // Continue with next question
                UI.updateQuestion(questionText);
                UI.updateTopic(result.topic);
                UI.updateQuestionCounter(AppState.questionCount + 1);

                // Speak only the clean question
                await Utils.sleep(500);
                await TTS.speak(questionText);
            }

        } catch (error) {
            console.error('Submit error:', error);
            Toast.error(error.message || 'Failed to submit answer');
        } finally {
            UI.setButtonLoading(submitBtn, false, 'Submit Answer');
        }
    },

    handleEndInterview() {
        if (confirm('Are you sure you want to end the interview? Your progress will be lost.')) {
            TTS.stop();
            SpeechRecognition.stop();
            Utils.clearSession();
            UI.showSection('hero');
            this.resetUploadForm();
            Toast.info('Interview ended');
        }
    },

    resetUploadForm() {
        AppState.resumeFile = null;
        AppState.jdFile = null;

        // Reset dropzones
        document.getElementById('resume-dropzone').classList.remove('file-selected');
        document.getElementById('jd-dropzone').classList.remove('file-selected');
        document.getElementById('resume-filename').textContent = 'Drop your resume here or click to browse';
        document.getElementById('jd-filename').textContent = 'Drop the JD here or click to browse';
        document.getElementById('resume-input').value = '';
        document.getElementById('jd-input').value = '';

        // Reset submit button
        const submitBtn = document.getElementById('btn-submit-docs');
        submitBtn.disabled = true;
        submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
    },

    /**
     * Load and display enhanced resume content
     */
    async loadEnhancedResume() {
        const contentEl = document.getElementById('enhanced-resume-content');
        const loadingEl = document.getElementById('enhancer-loading');

        try {
            loadingEl.classList.remove('hidden');
            contentEl.innerHTML = '<p class="text-gray-400">Loading enhanced resume...</p>';

            const result = await API.getEnhancedResume();

            if (result.status === 'success') {
                // Store content for download
                AppState.enhancedResumeContent = result.content;

                // Simple markdown to HTML conversion
                const htmlContent = this.markdownToHtml(result.content);
                contentEl.innerHTML = htmlContent;

                Toast.success('Enhanced resume loaded!');
            } else {
                contentEl.innerHTML = '<p class="text-red-400">Failed to load enhanced resume.</p>';
            }
        } catch (error) {
            console.error('Load enhanced resume error:', error);
            contentEl.innerHTML = `<p class="text-red-400">${error.message}</p>`;
        } finally {
            loadingEl.classList.add('hidden');
        }
    },

    /**
     * Download enhanced resume as markdown file
     */
    downloadEnhancedResume() {
        if (!AppState.enhancedResumeContent) {
            Toast.warning('Please wait for the resume to load first.');
            return;
        }

        // Create blob and download
        const blob = new Blob([AppState.enhancedResumeContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'enhanced_resume.md';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        Toast.success('Resume downloaded!');
    },

    /**
     * Simple markdown to HTML converter
     */
    markdownToHtml(markdown) {
        if (!markdown) return '';

        let html = markdown
            // Headers
            .replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold text-white mt-4 mb-2">$1</h3>')
            .replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold text-white mt-6 mb-3">$1</h2>')
            .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold text-white mt-6 mb-4">$1</h1>')
            // Bold
            .replace(/\*\*(.*?)\*\*/gim, '<strong class="font-semibold text-white">$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/gim, '<em>$1</em>')
            // Lists
            .replace(/^\- (.*$)/gim, '<li class="ml-4 text-gray-300">• $1</li>')
            .replace(/^\* (.*$)/gim, '<li class="ml-4 text-gray-300">• $1</li>')
            // Line breaks
            .replace(/\n\n/gim, '</p><p class="text-gray-300 mb-3">')
            .replace(/\n/gim, '<br>');

        return `<div class="text-gray-300">${html}</div>`;
    }
};

// ============================================
// Initialize on DOM Ready
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    InterviewApp.init();
});
