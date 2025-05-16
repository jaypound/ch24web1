/**
 * Content Report JavaScript
 * 
 * This script handles the dynamic functionality of the content report page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    const filterForm = document.getElementById('filterForm');
    const searchInput = document.getElementById('search');
    const channelSelect = document.getElementById('channel_name');
    const programSelect = document.getElementById('program_name');
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const sortSelect = document.getElementById('sort');
    const clearFiltersBtn = document.querySelector('a[href*="clear-filters"]');
    const detailsModal = document.getElementById('episodeDetailsModal');
    
    // Initialize Bootstrap modal
    let episodeModal = null;
    if (detailsModal) {
        episodeModal = new bootstrap.Modal(detailsModal);
    }
    
    // Auto-submit form when select fields change
    const autoSubmitElements = [channelSelect, programSelect, sortSelect];
    autoSubmitElements.forEach(element => {
        if (element) {
            element.addEventListener('change', () => {
                filterForm.submit();
            });
        }
    });
    
    // Debounced search input (delay submission while typing)
    let searchTimeout;
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterForm.submit();
            }, 500); // 500ms delay
        });
    }
    
    // Date range filtering
    const dateInputs = [startDateInput, endDateInput];
    dateInputs.forEach(input => {
        if (input) {
            input.addEventListener('change', () => {
                // Validate date range before submitting
                if (startDateInput && endDateInput && 
                    startDateInput.value && endDateInput.value) {
                    const startDate = new Date(startDateInput.value);
                    const endDate = new Date(endDateInput.value);
                    
                    if (startDate > endDate) {
                        alert('Start date cannot be after end date');
                        input.value = ''; // Clear the invalid input
                        return;
                    }
                }
                
                filterForm.submit();
            });
        }
    });
    
    // Handle "View Details" button clicks
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('view-details') || 
            e.target.closest('.view-details')) {
            
            e.preventDefault();
            
            // Get the button or its parent
            const button = e.target.classList.contains('view-details') ? 
                e.target : e.target.closest('.view-details');
            
            const episodeId = button.dataset.episodeId;
            
            if (episodeId && episodeModal) {
                // Show the modal with loading indicator
                episodeModal.show();
                
                // Update modal title
                const modalTitle = detailsModal.querySelector('.modal-title');
                if (modalTitle) {
                    modalTitle.textContent = 'Loading Episode Details...';
                }
                
                // Show loading spinner
                const modalContent = detailsModal.querySelector('#episodeDetailsContent');
                if (modalContent) {
                    modalContent.innerHTML = `
                        <div class="text-center py-5">
                            <div class="spinner-border" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p class="mt-2">Loading episode details...</p>
                        </div>
                    `;
                }
                
                // Fetch episode details from API
                fetchEpisodeDetails(episodeId);
            }
        }
    });
    
    /**
     * Fetch episode details from the API
     * @param {string} episodeId - The ID of the episode to fetch
     */
    function fetchEpisodeDetails(episodeId) {
        fetch(`/api/episodes/${episodeId}/details/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                // Update modal with episode data
                updateEpisodeDetailsModal(data);
            })
            .catch(error => {
                // Show error in modal
                const modalContent = detailsModal.querySelector('#episodeDetailsContent');
                if (modalContent) {
                    modalContent.innerHTML = `
                        <div class="alert alert-danger">
                            <h5>Error Loading Episode Details</h5>
                            <p>${error.message || 'An unknown error occurred'}</p>
                        </div>
                    `;
                }
                
                console.error('Error fetching episode details:', error);
            });
    }
    
    /**
     * Update the modal with episode details
     * @param {Object} episodeData - The episode data from the API
     */
    function updateEpisodeDetailsModal(episodeData) {
        // Update modal title
        const modalTitle = detailsModal.querySelector('.modal-title');
        if (modalTitle) {
            modalTitle.textContent = `${episodeData.title} (Episode ${episodeData.episode_number})`;
        }
        
        // Format the episode details HTML
        const modalContent = detailsModal.querySelector('#episodeDetailsContent');
        if (modalContent) {
            // Format the topics as badges
            const topicsBadges = episodeData.ai_topics && episodeData.ai_topics.length 
                ? episodeData.ai_topics.map(topic => 
                    `<span class="badge bg-secondary topic-badge">${topic}</span>`).join(' ')
                : '<span class="text-muted">No topics available</span>';
            
            // Format dates
            const createdDate = new Date(episodeData.created_at).toLocaleString();
            const lastScheduledDate = episodeData.last_scheduled 
                ? new Date(episodeData.last_scheduled).toLocaleString()
                : 'Never';
            
            // Build the HTML with bootstrap styling
            modalContent.innerHTML = `
                <div class="episode-details-container">
                    <!-- Header section -->
                    <div class="episode-details-header mb-4">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <h4 class="mb-1">${episodeData.title}</h4>
                                <p class="mb-0 text-muted">
                                    Episode ${episodeData.episode_number} • ${episodeData.program.program_name} • 
                                    ${createdDate} • 
                                    ${episodeData.duration_timecode || 'No duration'}
                                </p>
                            </div>
                            <div class="col-md-4 text-md-end mt-3 mt-md-0">
                                <span class="badge bg-primary fs-6">${episodeData.ai_age_rating || 'No rating'}</span>
                                <div class="mt-2">
                                    <small class="text-muted">
                                        Scheduled ${episodeData.schedule_count || 0} times
                                        ${episodeData.last_scheduled ? ' • Last: ' + lastScheduledDate : ''}
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="row">
                        <!-- Left column -->
                        <div class="col-md-5">
                            <div class="episode-details-section">
                                <h6>Creator Information</h6>
                                <table class="table table-sm">
                                    <tr>
                                        <th style="width: 120px;">Channel Name</th>
                                        <td>${episodeData.program.creator.channel_name}</td>
                                    </tr>
                                    <tr>
                                        <th>Creator</th>
                                        <td>${episodeData.program.creator.first_name} ${episodeData.program.creator.last_name}</td>
                                    </tr>
                                    <tr>
                                        <th>Program</th>
                                        <td>${episodeData.program.program_name}</td>
                                    </tr>
                                </table>
                            </div>

                            <div class="episode-details-section">
                                <h6>Episode Metadata</h6>
                                <table class="table table-sm">
                                    <tr>
                                        <th style="width: 120px;">Episode #</th>
                                        <td>${episodeData.episode_number}</td>
                                    </tr>
                                    <tr>
                                        <th>Uploaded</th>
                                        <td>${createdDate}</td>
                                    </tr>
                                    <tr>
                                        <th>Duration</th>
                                        <td>${episodeData.duration_timecode || 'Not available'}</td>
                                    </tr>
                                    <tr>
                                        <th>Schedule Count</th>
                                        <td>${episodeData.schedule_count || 0}</td>
                                    </tr>
                                    <tr>
                                        <th>Last Scheduled</th>
                                        <td>${lastScheduledDate}</td>
                                    </tr>
                                </table>
                            </div>

                            <div class="episode-details-section">
                                <h6>Topics</h6>
                                <div>
                                    ${topicsBadges}
                                </div>
                            </div>
                        </div>

                        <!-- Right column -->
                        <div class="col-md-7">
                            <div class="episode-details-section">
                                <h6>Description</h6>
                                <p class="mb-0">${episodeData.description || '<span class="text-muted">No description available</span>'}</p>
                            </div>

                            <div class="episode-details-section">
                                <h6>AI Summary</h6>
                                <p class="mb-0">${episodeData.ai_summary || '<span class="text-muted">No AI summary available</span>'}</p>
                            </div>

                            <div class="episode-details-section">
                                <h6>Actions</h6>
                                <div class="d-flex gap-2">
                                    <a href="/episode-analysis/${episodeData.custom_id}" class="btn btn-primary">
                                        <i class="bi bi-graph-up"></i> View Analysis
                                    </a>
                                    <a href="/view-episode/${episodeData.custom_id}" class="btn btn-primary">
                                        <i class="bi bi-play-circle"></i> Preview
                                    </a>
                                    <a href="/update-analysis/${episodeData.custom_id}" class="btn btn-primary">
                                        <i class="bi bi-arrow-repeat"></i> Update Analysis
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    }
});