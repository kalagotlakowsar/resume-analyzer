/* ===================================================================
   AI Resume Analyzer - Main JavaScript File
   =================================================================== */

document.addEventListener('DOMContentLoaded', function () {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Upload Drag & Drop Handlers
    const dropzone = document.getElementById('uploadDropzone');
    const fileInput = document.getElementById('resume_file_input');
    const fileInfoBox = document.getElementById('selectedFileInfo');
    const fileNameDisplay = document.getElementById('selectedFileName');
    const fileSizeDisplay = document.getElementById('selectedFileSize');

    if (dropzone && fileInput) {
        // Clicking dropzone triggers file input
        dropzone.addEventListener('click', () => fileInput.click());

        // Dragover styling
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            }, false);
        });

        // Drop event handler
        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length > 0) {
                fileInput.files = files;
                updateFileDisplay(files[0]);
            }
        });

        // File input change handler
        fileInput.addEventListener('change', function () {
            if (this.files && this.files.length > 0) {
                updateFileDisplay(this.files[0]);
            }
        });
    }

    function updateFileDisplay(file) {
        if (!fileInfoBox || !fileNameDisplay) return;
        fileNameDisplay.textContent = file.name;
        const sizeKB = (file.size / 1024).toFixed(1);
        fileSizeDisplay.textContent = `${sizeKB} KB`;
        fileInfoBox.classList.remove('d-none');
    }

    // Role Selector AJAX Preview
    const roleSelect = document.getElementById('id_job_role');
    const rolePreviewContainer = document.getElementById('rolePreviewContainer');
    const rolePreviewTitle = document.getElementById('rolePreviewTitle');
    const rolePreviewSkills = document.getElementById('rolePreviewSkills');

    if (roleSelect && rolePreviewContainer) {
        roleSelect.addEventListener('change', function () {
            const roleId = this.value;
            if (!roleId) {
                rolePreviewContainer.classList.add('d-none');
                return;
            }

            fetch(`/api/role-skills/${roleId}/`)
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        rolePreviewTitle.textContent = `${data.title} (${data.min_experience_years}+ years exp)`;
                        rolePreviewSkills.innerHTML = '';
                        
                        // Render required skills
                        data.required_skills.forEach(sk => {
                            const badge = document.createElement('span');
                            badge.className = 'skill-pill skill-matched';
                            badge.textContent = `✓ ${sk.name}`;
                            rolePreviewSkills.appendChild(badge);
                        });

                        // Render preferred skills
                        data.preferred_skills.forEach(sk => {
                            const badge = document.createElement('span');
                            badge.className = 'skill-pill skill-recommended';
                            badge.textContent = `+ ${sk.name}`;
                            rolePreviewSkills.appendChild(badge);
                        });

                        rolePreviewContainer.classList.remove('d-none');
                    }
                })
                .catch(err => console.error('Error fetching role skills:', err));
        });
    }

    // Show Loading Spinner on Resume Submit
    const uploadForm = document.getElementById('resumeUploadForm');
    const submitBtn = document.getElementById('btnSubmitAnalyze');
    const loadingOverlay = document.getElementById('analyzeLoadingOverlay');

    if (uploadForm && submitBtn) {
        uploadForm.addEventListener('submit', function (e) {
            if (fileInput && fileInput.files.length === 0) {
                // If native validation fails
                return;
            }
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Analyzing Resume with AI...`;
            if (loadingOverlay) {
                loadingOverlay.classList.remove('d-none');
            }
        });
    }
});
