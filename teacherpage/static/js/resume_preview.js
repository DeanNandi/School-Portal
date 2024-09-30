// resume_preview.js

$(document).ready(function() {
    // Variables for managing form navigation
    var current_fs, next_fs, previous_fs; // fieldsets
    var opacity;
    var current = 1;
    var steps = $("fieldset").length;

    // Initialize progress bar
    setProgressBar(current);

    // Handle "Next" button click
    $(".next").click(function() {
        current_fs = $(this).parent();
        next_fs = $(this).parent().next();

        // Add "active" class to the next step in the progress bar
        $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

        // Show the next fieldset
        next_fs.show();
        // Hide the current fieldset with a fade out effect
        current_fs.animate({opacity: 0}, {
            step: function(now) {
                opacity = 1 - now;
                current_fs.css({
                    'display': 'none',
                    'position': 'relative'
                });
                next_fs.css({'opacity': opacity});
            },
            duration: 500
        });
        setProgressBar(++current);
    });

    // Handle "Previous" button click
    $(".previous").click(function() {
        current_fs = $(this).parent();
        previous_fs = $(this).parent().prev();

        // Remove "active" class from current step in the progress bar
        $("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");

        // Show the previous fieldset
        previous_fs.show();
        // Hide the current fieldset with a fade out effect
        current_fs.animate({opacity: 0}, {
            step: function(now) {
                opacity = 1 - now;
                current_fs.css({
                    'display': 'none',
                    'position': 'relative'
                });
                previous_fs.css({'opacity': opacity});
            },
            duration: 500
        });
        setProgressBar(--current);
    });

    // Function to update the progress bar
    function setProgressBar(curStep) {
        var percent = parseFloat(100 / steps) * curStep;
        percent = percent.toFixed();
        $(".progress-bar").css("width", percent + "%");
    }

    // Prevent default form submission on "Submit" button click
    $(".submit").click(function() {
        return false;
    });

    // Handle "Preview Resume" button click
    $('#previewButton').click(function() {
        populateModal();
        $('#resumePreviewModal').modal('show');
    });

    // Intercept form submission
    $('form').submit(function(e) {
        e.preventDefault();
        // Show the preview modal before submitting
        $('#previewButton').click();
    });

    // Handle final submission after modal review
    $('#resumePreviewModal .btn-primary').click(function() {
        $('#resumePreviewModal').modal('hide');
        submitForm();
    });
});

// Function to populate the preview modal with form data
function populateModal() {
    // Personal Information
    $('#previewName').text(getFieldValue('input[name="First_Name"]') + ' ' + getFieldValue('input[name="Last_Name"]'));
    $('#previewContact').text(getFieldValue('input[name="email_address"]') + ' • ' + getFieldValue('input[name="phone_number"]'));

    // Set the photo
    var photoUrl = $('#candidatePhoto').attr('src');
    if (photoUrl && photoUrl !== '') {
        $('#previewPhoto').attr('src', photoUrl).show();
    } else {
        $('#previewPhoto').hide();
    }

    // Professional Summary
    $('#previewSummary p').text(getFieldValue('#id_summary'));

    // Work Experience
    $('#previewExperience').html('<h2>Experience</h2>' + formatExperience(getFieldValue('#id_work_experiences')));

    // Education
    $('#previewEducation').html('<h2>Education</h2>' + formatEducation(getFieldValue('#id_educations')));

    // Certifications
    $('#previewCertifications').html('<h2>Certifications</h2>' + formatList(getFieldValue('#id_certifications')));

    // Skills
    $('#previewSkills').html('<h2>Skills</h2>' +
        '<h3>Technical Skills</h3>' + formatList(getFieldValue('#id_technical_skills')) +
        '<h3>Soft Skills</h3>' + formatList(getFieldValue('#id_soft_skills'))
    );

    // Languages
    $('#previewLanguages').html('<h2>Languages</h2>' + formatList(getFieldValue('#id_languages')));

    // Interests
    $('#previewInterests').html('<h2>Interests and Hobbies</h2>' + formatList(getFieldValue('#id_interests')));

    // References
    $('#previewReferences').html('<h2>References</h2>' + formatReferences(getFieldValue('#id_references')));
}

// Add this function to get the candidate's photo URL
function getCandidatePhotoUrl() {
    return $('#candidatePhoto').attr('src');
}

// Function to format work experience entries
function formatExperience(experience) {
    if (!experience) return '<p>No work experience provided</p>';
    let items = experience.split('\n\n');
    return items.map(item => {
        let lines = item.split('\n');
        return `
            <div class="experience-item">
                <h3>${lines[0]}</h3>
                <p>${lines[1]}</p>
                <ul>
                    ${lines.slice(2).map(line => `<li>${line}</li>`).join('')}
                </ul>
            </div>
        `;
    }).join('');
}

// Function to format education entries
function formatEducation(education) {
    if (!education) return '<p>No education information provided</p>';
    let items = education.split('\n\n');
    return items.map(item => {
        let lines = item.split('\n');
        return `
            <div class="education-item">
                <h3>${lines[0]}</h3>
                <p>${lines[1]}</p>
                <p>${lines[2] || ''}</p>
            </div>
        `;
    }).join('');
}

// Function to format list items (used for skills, languages, interests)
function formatList(items) {
    if (!items) return '<p>No information provided</p>';
    let listItems = items.split('\n');
    return '<ul>' + listItems.map(item => `<li>${item}</li>`).join('') + '</ul>';
}

// Function to format references
function formatReferences(references) {
    if (!references) return '<p>No references provided</p>';
    let items = references.split('\n\n');
    return items.map(item => {
        let lines = item.split('\n');
        return `
            <div class="reference-item">
                <h3>${lines[0]}</h3>
                <p>${lines[1]}</p>
            </div>
        `;
    }).join('');
}

// Helper function to safely get form field values
function getFieldValue(selector) {
    const field = $(selector);
    return field.length ? field.val() : '';
}

// Function to show notification messages
function showNotification(message, isError = false) {
    $('#notificationMessage').text(message);
    var notification = $('#notification');
    notification.removeClass('error');
    if (isError) {
        notification.addClass('error');
    }
    notification.fadeIn(300);
    // Automatically hide the notification after 5 seconds
    setTimeout(function() {
        notification.fadeOut(300);
    }, 5000);
}

// Function to submit the form via AJAX
function submitForm() {
    var formData = new FormData($('form')[0]);

    // Add the photo URL to the form data
    formData.append('photo_url', getCandidatePhotoUrl());


    $.ajax({
        url: $('form').attr('action'),
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function(response) {
            if (response.success) {
                showNotification('Your resume has been successfully updated!');
                // Scroll to the top of the form to ensure the notification is visible
                $('html, body').animate({
                    scrollTop: $("#notification").offset().top - 100
                }, 500);
                // Wait for 2 seconds before redirecting to allow the user to see the notification
                setTimeout(function() {
                    window.location.href = '/studentpage/manage-resume/';
                }, 2000);
            } else {
                showNotification('There was an error updating your resume. Please try again.', true);
                if (response.errors) {
                    console.log('Form errors:', response.errors);
                    // You can display these errors in the form or in a modal
                }
            }
        },
        error: function() {
            showNotification('An error occurred. Please try again later.', true);
        }
    });
}

// Initialize Bootstrap modal
// Make sure this code runs after the DOM is fully loaded
document.addEventListener('DOMContentLoaded', (event) => {
    var resumePreviewModal = new bootstrap.Modal(document.getElementById('resumePreviewModal'));
});