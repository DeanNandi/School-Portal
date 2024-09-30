// Navigation js
$(document).ready(function () {
    const progressSteps = document.querySelectorAll('#progressbar li');
    const fieldsets = document.querySelectorAll('fieldset');

    function navigateToStep(clickedIndex) {
        // Hide all fieldsets and remove 'active' class from all steps
        fieldsets.forEach((fieldset, index) => {
            fieldset.style.display = 'none'; // Hide all fieldsets
            if (index <= clickedIndex) {
                progressSteps[index].classList.add('active'); // Mark previous steps as active
            } else {
                progressSteps[index].classList.remove('active'); // Ensure next steps are not marked active
            }
        });

        // Show the fieldset corresponding to the clicked step
        fieldsets[clickedIndex].style.display = 'block';
    }

    // Attach click event listeners to each step in the progress bar
    progressSteps.forEach((step, index) => {
        step.addEventListener('click', () => {
            navigateToStep(index);
        });
    });

    // Updated next and previous button functionality to keep them synchronized with the progress bar
    $(".next").click(function () {
        let current_fs = $(this).parent();
        let next_fs = $(this).parent().next();
        let currentStepIndex = $("fieldset").index(current_fs);

        // Activate the next step on the progress bar
        $("#progressbar li").eq(currentStepIndex + 1).addClass('active');

        // Show the next fieldset
        next_fs.show();
        current_fs.hide(); // Ensure the current fieldset is hidden
    });

    $(".previous").click(function () {
        let current_fs = $(this).parent();
        let previous_fs = $(this).parent().prev();
        let currentStepIndex = $("fieldset").index(current_fs);

        // Deactivate the current step and activate the previous step on the progress bar
        $("#progressbar li").eq(currentStepIndex).removeClass('active');

        // Show the previous fieldset
        previous_fs.show();
        current_fs.hide(); // Ensure the current fieldset is hidden
    });
});

// end of navigation

// download js

let profileImageDataURL = '';
    
// Convert the uploaded profile picture to a Data URL
// Convert the uploaded profile picture to a Data URL
document.getElementById('profile-upload').addEventListener('change', function(event) {
const file = event.target.files[0];
const reader = new FileReader();

reader.onload = function(e) {
profileImageDataURL = e.target.result; // Save the image as a Data URL
cropImageToCircle(profileImageDataURL, function(croppedImageDataURL) {
    document.getElementById('cv-image').src = croppedImageDataURL; // Display the cropped image in the preview
    profileImageDataURL = croppedImageDataURL; // Update to use the cropped image for the PDF
});
};

if (file) {
reader.readAsDataURL(file);
}
});


// Function to crop image to a circle
function cropImageToCircle(imageDataURL, callback) {
const img = new Image();
img.onload = function() {
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
const size = Math.min(img.width, img.height);

canvas.width = size;
canvas.height = size;

ctx.beginPath();
ctx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2, true);
ctx.closePath();
ctx.clip();

ctx.drawImage(img, (img.width - size) / 2, (img.height - size) / 2, size, size, 0, 0, size, size);

const croppedImageDataURL = canvas.toDataURL('image/png');
callback(croppedImageDataURL);
};

img.src = imageDataURL;
}


async function downloadPDF() {
    const { jsPDF } = window.jspdf;

    const doc = new jsPDF();

    const fullName = document.getElementById('preview-name').value;
    const jobTitle = document.getElementById('preview-title').value;
    const summary = document.getElementById('preview-summary').value;
    const contacts = document.getElementById('preview-contacts').value;

    const experienceList = Array.from(document.querySelectorAll('#experience-list > div')).map(div => div.innerText);
    const educationList = Array.from(document.querySelectorAll('#education-list > div')).map(div => div.innerText);
    const certificationsList = Array.from(document.querySelectorAll('#certifications-list li')).map(li => li.innerText);
    const skillsList = Array.from(document.querySelectorAll('#skills-list li')).map(li => li.innerText);
    const languagesList = Array.from(document.querySelectorAll('#Languages-list li')).map(li => li.innerText);
    const hobbiesList = Array.from(document.querySelectorAll('#Interests\\ and\\ Hobbies-list li')).map(li => li.innerText);
    const referencesList = Array.from(document.querySelectorAll('#References-list li')).map(li => li.innerText);

    const educationEntries = document.querySelectorAll('#education .education-item');
    const experienceEntries = document.querySelectorAll('.work-experience-entry');

    let y = 10; // Start position on the PDF

    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 10; // Margin on both sides
    const contentWidth = pageWidth - margin * 2; // Maximum width for content
    const imageWidth = 40;
    const imageX = (pageWidth - imageWidth) / 2;

    if (profileImageDataURL) {
doc.addImage(profileImageDataURL, 'PNG', imageX, y, imageWidth, imageWidth);
y += 50;
}

    doc.setFontSize(20);
    doc.setTextColor('#0b3484'); // Header color for the full name
    doc.setFont("helvetica", "bold");
    const textWidth = doc.getTextWidth(fullName);
    doc.text(fullName, (pageWidth - textWidth) / 2, y);
    y += 7;

    doc.setFontSize(15);
    doc.setTextColor('#93c9f6'); // Header color for job title
    const jobTitleWidth = doc.getTextWidth(jobTitle);
    doc.text(jobTitle, (pageWidth - jobTitleWidth) / 2, y);
    y += 5;

    doc.setFontSize(12);
    doc.setTextColor('#000000'); // Set text color for normal entries
    const contactsWidth = doc.getTextWidth(contacts);
    doc.text(contacts, (pageWidth - contactsWidth) / 2, y);
    y += 10;

    function addCenteredHeaderWithUnderline(text) {
        if (y + 20 > doc.internal.pageSize.height) {
            doc.addPage();
            y = 10;
        }
        doc.setFontSize(16);
        doc.setTextColor('#007bff'); // Header color
        const headerWidth = doc.getTextWidth(text);
        doc.setLineWidth(0.5);
        doc.text(text, (pageWidth - headerWidth) / 2, y);
        doc.setDrawColor('#007bff');
        doc.line(margin, y + 1, pageWidth - margin, y + 1);
        y += 10;
    }

    function addContentToPDF(contentList, spacing = 7) {
        contentList.forEach(content => {
            const lines = doc.splitTextToSize(content, contentWidth); // Split text to fit the content width
            lines.forEach(line => {
                if (y + spacing > doc.internal.pageSize.height) {
                    doc.addPage();
                    y = 10;
                }
                doc.text(line, margin, y);
                y += spacing;
            });
        });
    }

    function addBulletListToPDF(contentList) {
contentList.forEach(content => {
    if (y + 10 > doc.internal.pageSize.height) {
        doc.addPage();
        y = 10;
    }
    doc.setFont('Arial', 'normal');
    doc.setFontSize(12); // Match the font size used elsewhere
    doc.setTextColor(51, 51, 51); // Set text color to black (#333 in RGB)
    doc.text(`• ${content}`, margin, y); // Add bullet point
    y += 5; // Increase y position for the next line
});
}            // Add sections to the PDF
function addEducationToPDF(entries) {
addCenteredHeaderWithUnderline('Education');
entries.forEach(entry => {
    const school = entry.querySelector('input[name="school[]"]').value.trim();
    const qualification = entry.querySelector('input[name="qualification[]"]').value.trim();
    const tenure = entry.querySelector('input[name="tenure[]"]').value.trim();

    if (y + 20 > doc.internal.pageSize.height) {
        doc.addPage();
        y = 10;
    }
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(14);
    doc.setTextColor(51, 51, 51); // Set text color to black (#333 in RGB)
    doc.text(school, margin, y); // School name

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(12);
    doc.text(qualification, margin, y + 7); // Qualification

    const tenureWidth = doc.getTextWidth(tenure.trim());
    doc.text(tenure.trim(), pageWidth - margin - tenureWidth, y + 7); // Tenure at the right side

    y += 15;
});
}

function addExperienceToPDF(entries) {
addCenteredHeaderWithUnderline('Experience');
const pageWidth = doc.internal.pageSize.width;
const margin = 10; // Assuming a margin of 10

entries.forEach(entry => {
const company = entry.querySelector('input[name="company[]"]').value.trim();
const role = entry.querySelector('input[name="role[]"]').value.trim();
const tenure = entry.querySelector('input[name="tenure[]"]').value.trim();
const responsibilities = entry.querySelector('textarea[name="responsibilities[]"]').value.trim().split('\n');

if (y + 20 > doc.internal.pageSize.height) {
    doc.addPage();
    y = 10;
}

doc.setFont('helvetica', 'bold');
doc.setFontSize(14);
doc.setTextColor(51, 51, 51); // Set text color to black (#333 in RGB)
doc.text(company, margin, y); // Company name

doc.setFont('helvetica', 'normal');
doc.setFontSize(12);
doc.text(role, margin, y + 7); // Role

const tenureWidth = doc.getTextWidth(tenure.trim());
doc.text(tenure.trim(), pageWidth - margin - tenureWidth, y + 7); // Tenure at the right side

y += 15;

responsibilities.forEach(responsibility => {
    const wrappedText = doc.splitTextToSize(`• ${responsibility}`, pageWidth - margin * 2 - 5);

    wrappedText.forEach(line => {
        if (y + 10 > doc.internal.pageSize.height) {
            doc.addPage();
            y = 10;
        }
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(12);
        doc.text(line, margin + 5, y);
        y += 7;
    });

    y += 1; // Space between different responsibility entries
});

y += 5; // Space between different experience entries
});
}


// Calculate the height required for the summary
addCenteredHeaderWithUnderline('Professional Summary');
doc.setFontSize(14);
doc.setFont('Arial', 'normal');
doc.setTextColor(51, 51, 51); // Set text color to black (#333)
const summaryLines = doc.splitTextToSize(summary, contentWidth);
addContentToPDF(summaryLines, 7);

addExperienceToPDF(experienceEntries);
//addCenteredHeaderWithUnderline('Experience');
//addContentToPDF(experienceList, 10);

addEducationToPDF(educationEntries);
//addCenteredHeaderWithUnderline('Education');
//addEducationToPDF(educationList, 10);

addCenteredHeaderWithUnderline('Certifications');
addBulletListToPDF(certificationsList, 10); // Use the bullet list function

addCenteredHeaderWithUnderline('Skills');
addBulletListToPDF(skillsList, 10);

addCenteredHeaderWithUnderline('Languages');
addBulletListToPDF(languagesList, 10);

addCenteredHeaderWithUnderline('Interests and Hobbies');
addBulletListToPDF(hobbiesList, 10);

addCenteredHeaderWithUnderline('References');
addBulletListToPDF(referencesList, 10);

// Save the PDF file
doc.save(`${fullName}_Resume.pdf`);
}


// end of download js

//data manipulation js

document.addEventListener('DOMContentLoaded', function () {
    const addAnotherReferenceButton = document.querySelector('#references .add-another');
    const referencesList = document.getElementById('References-list'); // Make sure you have an element with this ID in your HTML where you want to display the references

    function updateReferencesPreview() {
        // Clear previous entries
        referencesList.innerHTML = '';

        // Get all reference entries
        const referenceEntries = document.querySelectorAll('.referees-item');

        referenceEntries.forEach(entry => {
            const referee = entry.querySelector('input[name="Referees[]"]').value.trim();
            const company = entry.querySelector('input[name="Company[]"]').value.trim();
            const contact = entry.querySelector('input[name="contact[]"]').value.trim();

            // Create a new reference block
            if (referee && company && contact) {
                const referenceItem = document.createElement('li');
                referenceItem.textContent = `${referee} from ${company} - Contact: ${contact}`;
                referencesList.appendChild(referenceItem);
            }
        });
    }

    function attachReferenceInputListeners() {
        document.querySelectorAll('.referees-item input').forEach(input => {
            input.removeEventListener('input', updateReferencesPreview); // Avoid multiple bindings
            input.addEventListener('input', updateReferencesPreview);
        });
    }

    // Listen for changes in the references fields
    attachReferenceInputListeners();

    // Update the preview when a new reference entry is added
    addAnotherReferenceButton.addEventListener('click', function () {
        setTimeout(() => {
            attachReferenceInputListeners();
            updateReferencesPreview(); // Update preview immediately after adding a new entry
        }, 100); // Short delay to ensure the new entry is added
    });

    // Listen for delete button clicks
    $(document).on('click', '.delete-btn', function() {
        $(this).parent().remove();
        updateReferencesPreview();
    });

    // Initialize preview with any existing data
    updateReferencesPreview();
});

document.addEventListener('DOMContentLoaded', function () {
    const addAnotherHobbyButton = document.querySelector('#hobbies-languages .add-another');
    const hobbiesList = document.getElementById('Interests and Hobbies-list'); // Make sure you have an element with this ID in your HTML where you want to display the hobbies

    function updateHobbiesPreview() {
        // Clear previous entries
        hobbiesList.innerHTML = '';

        // Get all hobby entries
        const hobbyEntries = document.querySelectorAll('.hobbies-container input[name="hobbies[]"]');

        hobbyEntries.forEach(entry => {
            const hobby = entry.value.trim();

            // Create a new hobby block, assuming you want each hobby to be shown as a list item
            if (hobby) {
                const hobbyItem = document.createElement('li');
                hobbyItem.textContent = hobby;
                hobbiesList.appendChild(hobbyItem);
            }
        });
    }

    function attachHobbyInputListeners() {
        document.querySelectorAll('.hobbies-container input').forEach(input => {
            input.removeEventListener('input', updateHobbiesPreview); // Avoid multiple bindings
            input.addEventListener('input', updateHobbiesPreview);
        });
    }

    // Listen for changes in the hobbies fields
    attachHobbyInputListeners();

    // Update the preview when a new hobby entry is added
    addAnotherHobbyButton.addEventListener('click', function() {
        setTimeout(() => {
            attachHobbyInputListeners();
            updateHobbiesPreview(); // Update preview immediately after adding a new entry
        }, 100); // Short delay to ensure the new entry is added
    });

    // Listen for delete button clicks
    $(document).on('click', '.delete-btn', function() {
        $(this).parent().remove();
        updateHobbiesPreview();
    });

    // Initialize preview with any existing data
    updateHobbiesPreview();
});

document.addEventListener('DOMContentLoaded', function () {
    const addAnotherLanguageButton = document.querySelector('#languages .add-another');
    const languagesList = document.getElementById('Languages-list'); // Make sure you have an element with this ID in your HTML where you want to display the languages

    function updateLanguagesPreview() {
        // Clear previous entries
        languagesList.innerHTML = '';

        // Get all language entries
        const languageEntries = document.querySelectorAll('.languages-container input[name="language[]"]');

        languageEntries.forEach(entry => {
            const language = entry.value.trim();

            // Create a new language block, assuming you want each language to be shown as a list item
            if (language) {
                const languageItem = document.createElement('li');
                languageItem.textContent = language;
                languagesList.appendChild(languageItem);
            }
        });
    }

    function attachLanguageInputListeners() {
        document.querySelectorAll('.languages-container input').forEach(input => {
            input.removeEventListener('input', updateLanguagesPreview); // Avoid multiple bindings
            input.addEventListener('input', updateLanguagesPreview);
        });
    }

    // Listen for changes in the languages fields
    attachLanguageInputListeners();

    // Update the preview when a new language entry is added
    addAnotherLanguageButton.addEventListener('click', function() {
        setTimeout(() => {
            attachLanguageInputListeners();
            updateLanguagesPreview(); // Update preview immediately after adding a new entry
        }, 100); // Short delay to ensure the new entry is added
    });

    // Listen for delete button clicks
    $(document).on('click', '.delete-btn', function() {
        $(this).parent().remove();
        updateLanguagesPreview();
    });

    // Initialize preview with any existing data
    updateLanguagesPreview();
});


document.addEventListener('DOMContentLoaded', function () {
    const addAnotherCertificationButton = document.querySelector('#certifications .add-another');
    const certificationsList = document.getElementById('certifications-list');

    function updateCertificationsPreview() {
        // Clear previous entries
        certificationsList.innerHTML = '';

        // Get all certification entries
        const certificationEntries = document.querySelectorAll('.certification-item input[name="certification[]"]');

        certificationEntries.forEach(entry => {
            const certification = entry.value.trim();

            // Create a new certification block, assuming you want each certification to be shown as a list item
            if (certification) {
                const certificationItem = document.createElement('li');
                certificationItem.textContent = certification;
                certificationsList.appendChild(certificationItem);
            }
        });
    }

    function attachCertificationInputListeners() {
        document.querySelectorAll('.certification-item input').forEach(input => {
            input.removeEventListener('input', updateCertificationsPreview); // Avoid multiple bindings
            input.addEventListener('input', updateCertificationsPreview);
        });
    }

    // Listen for changes in the certification fields
    attachCertificationInputListeners();

    // Update the preview when a new certification entry is added
    addAnotherCertificationButton.addEventListener('click', function() {
        setTimeout(() => {
            attachCertificationInputListeners();
            updateCertificationsPreview(); // Update preview immediately after adding a new entry
        }, 100); // Short delay to ensure the new entry is added
    });

    // Listen for delete button clicks
    $(document).on('click', '.delete-btn', function() {
        $(this).parent().remove();
        updateCertificationsPreview();
    });

    // Initialize preview with any existing data
    updateCertificationsPreview();
});

document.addEventListener('DOMContentLoaded', function() {
    const progressSteps = document.querySelectorAll('#progressbar li');
    const fieldsets = document.querySelectorAll('fieldset');

    function navigateToStep(clickedIndex) {
        // Hide all fieldsets and remove 'active' class from all steps
        fieldsets.forEach((fieldset, index) => {
            fieldset.style.display = 'none'; // Hide all fieldsets
            if (index <= clickedIndex) {
                progressSteps[index].classList.add('active'); // Mark previous steps as active
            } else {
                progressSteps[index].classList.remove('active'); // Ensure next steps are not marked active
            }
        });

        // Show the fieldset corresponding to the clicked step
        fieldsets[clickedIndex].style.display = 'block';
    }

    // Attach click event listeners to each step in the progress bar
    progressSteps.forEach((step, index) => {
        step.addEventListener('click', () => {
            navigateToStep(index);
        });
    });

    // Existing functionality for next and previous buttons
    $(".next").click(function() {
        let current_fs = $(this).parent();
        let next_fs = $(this).parent().next();
        let currentStepIndex = $("fieldset").index(current_fs);

        // Activate the next step on the progressbar
        $("#progressbar li").eq(currentStepIndex + 1).addClass('active');

        // Show the next fieldset
        next_fs.show();
        // Hide the current fieldset with style
        current_fs.animate({opacity: 0}, {
            step: function(now, mx) {
                let scale = 1 - (1 - now) * 0.2;
                let left = (now * 50) + "%";
                let opacity = 1 - now;
                current_fs.css({
                    'transform': 'scale(' + scale + ')',
                    'position': 'absolute'
                });
                next_fs.css({'left': left, 'opacity': opacity});
            },
            duration: 800,
            complete: function() {
                current_fs.hide();
                current_fs.css('position', 'relative');
            }
        });
    });

    $(".previous").click(function() {
        let current_fs = $(this).parent();
        let previous_fs = $(this).parent().prev();
        let currentStepIndex = $("fieldset").index(current_fs);

        // De-activate the current step and activate the previous step on the progressbar
        $("#progressbar li").eq(currentStepIndex).removeClass('active');

        // Show the previous fieldset
        previous_fs.show();
        current_fs.animate({opacity: 0}, {
            step: function(now, mx) {
                let scale = 0.8 + (1 - now) * 0.2;
                let left = ((1 - now) * 50) + "%";
                let opacity = 1 - now;
                current_fs.css({'left': left});
                previous_fs.css({'transform': 'scale(' + scale + ')', 'opacity': opacity});
            },
            duration: 800,
            complete: function() {
                current_fs.hide();
                current_fs.css('position', 'relative');
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('profile-summary');

    function adjustHeight(el) {
        el.style.height = 'auto';
        el.style.height = (el.scrollHeight) + 'px';
    }

    // Adjust height for Professional Summary textarea
    textarea.addEventListener('input', function() {
        adjustHeight(textarea);
    });

    // Adjust height for all Responsibilities textareas
    const responsibilitiesTextareas = document.querySelectorAll('textarea[name="responsibilities[]"]');
    responsibilitiesTextareas.forEach(function(textarea) {
        adjustHeight(textarea); // Initial adjustment
        textarea.addEventListener('input', function() {
            adjustHeight(textarea);
        });
    });

    // Adjust height for new Responsibilities textareas dynamically added
    document.querySelector('.add-another').addEventListener('click', function() {
        setTimeout(function() {
            const newTextareas = document.querySelectorAll('textarea[name="responsibilities[]"]');
            newTextareas.forEach(function(textarea) {
                textarea.removeEventListener('input', adjustHeight); // Avoid duplicate listeners
                textarea.addEventListener('input', function() {
                    adjustHeight(textarea);
                });
            });
        }, 100); // Delay to allow DOM update
    });

    // Initial adjustment on page load
    adjustHeight(textarea);
});

$(document).ready(function () {
    // Function to handle adding new sections with delete functionality
    function addNewSection(containerSelector, entryClass, buttonSelector) {
        $(buttonSelector).click(function () {
            var newEntry = $(containerSelector + ' ' + entryClass).first().clone(); // Clone the first entry
            newEntry.find('input').val(''); // Clear input fields
            newEntry.find('.delete-btn').remove(); // Remove any existing delete buttons in the clone
            newEntry.append('<button type="button" class="delete-btn">Delete</button>'); // Add a new delete button

            $(containerSelector).append(newEntry); // Append the new entry to the container

            // Add delete button functionality to the new entry
            newEntry.find('.delete-btn').click(function () {
                $(this).parent().remove();
            });
        });
    }

    // Initialize the functionality for Languages
    addNewSection('.languages-container', '.language-entry', '#languages .add-another');

    // Initialize the functionality for Interests and Hobbies
    addNewSection('.hobbies-container', '.hobby-entry', '#hobbies-languages .add-another');

    // Ensure delete buttons are functional for initial items
    $('.delete-btn').click(function () {
        $(this).parent().remove();
    });
});

$(document).ready(function () {
    function addReference() {
        // Clone the first '.referees-item', clear the input values, and ensure there's only one delete button
        var originalEntry = $('#references .referees-item').first().clone();
        originalEntry.find('input').val(''); // Clear the values in the cloned inputs
        originalEntry.find('.delete-btn').remove(); // Remove any existing delete buttons

        // Create a new delete button and append it to the cloned entry
        var deleteButton = $('<button type="button" class="delete-btn">Delete</button>');
        originalEntry.append(deleteButton);

        // Insert the new entry before the "Add Another" button
        $('#references .add-another').before(originalEntry);

        // Attach event to the new delete button in the cloned entry
        deleteButton.click(function() {
            $(this).parent().remove();
        });
    }

    // Attach the addReference function to the "Add Another" button
    $('#references .add-another').click(function() {
        addReference();
    });

    // Attach a click event handler for the initial delete button in the HTML
    $(document).on('click', '.delete-btn', function () {
        $(this).parent().remove();
    });
});

        document.getElementById('responsibilities').addEventListener('input', function() {
                const inputText = this.value;
                const lines = inputText.split('\n');
                const listItems = lines.map(line => `<li>${line}</li>`).join('');
                document.getElementById('responsibilities-list').innerHTML = listItems;
            });


        const textarea = document.getElementById('profile-summary');

        function adjustHeight(el) {
        el.style.height = 'auto';
        el.style.height = (el.scrollHeight) + 'px';
        }

        textarea.addEventListener('input', function() {
        adjustHeight(textarea);
        });

        // Initial adjustment on page load
        adjustHeight(textarea);

        document.getElementById('profile-upload').addEventListener('change', function(event) {
            const file = event.target.files[0];
            const reader = new FileReader();

            reader.onload = function(e) {
                document.getElementById('cv-image').src = e.target.result;
            }

            if (file) {
                reader.readAsDataURL(file);
            }
        });

        document.addEventListener('DOMContentLoaded', function () {
        const firstNameInput = document.getElementById('firstname');
        const lastNameInput = document.querySelector('input[name="lname"]');
        const previewName = document.getElementById('preview-name');
        const jobTitleInput = document.getElementById('job_title');
        const SummaryInput = document.getElementById('profile-summary');
        const emailInput= document.getElementById('email');
        const phoneInput = document.getElementById('phone');
        const nationalityInput = document.getElementById('nationality');
        
        const previewTitle = document.getElementById('preview-title');
        const previewSummary = document.getElementById('preview-summary');
        const previewContacts = document.getElementById('preview-contacts');
        
        
        function updatePreviewName() {
            const firstName = firstNameInput.value.trim();
            const lastName = lastNameInput.value.trim();
            previewName.value = `${firstName} ${lastName}`;
        }

        function updatePreviewContacts() {
            const email = emailInput.value.trim();
            const phone = phoneInput.value.trim();
            const nationality = nationalityInput.value.trim();
            previewContacts.value = `${email} • ${phone} • ${nationality}`;
        }

        function updatePreviewTitle() {
            const jobTitle = jobTitleInput.value.trim();
            previewTitle.value = `${jobTitle}`;
        }

        function updatePreviewSummary() {
            const Summary = SummaryInput.value.trim();
            previewSummary.value = `${Summary}`;
        }


        firstNameInput.addEventListener('input', updatePreviewName);
        lastNameInput.addEventListener('input', updatePreviewName);
        jobTitleInput.addEventListener('input', updatePreviewTitle);
        SummaryInput.addEventListener('input', updatePreviewSummary);
        emailInput.addEventListener('input', updatePreviewContacts);
        phoneInput.addEventListener('input', updatePreviewContacts);
        nationalityInput.addEventListener('input', updatePreviewContacts);
            });


        $(document).ready(function () {
            var current_fs, next_fs, previous_fs;
            var opacity;

            $(".next").click(function () {
                current_fs = $(this).parent();
                next_fs = $(this).parent().next();

                $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

                next_fs.show();
                current_fs.animate({ opacity: 0 }, {
                    step: function (now) {
                        opacity = 1 - now;
                        current_fs.css({
                            'display': 'none',
                            'position': 'relative'
                        });
                        next_fs.css({ 'opacity': opacity });
                    },
                    duration: 600
                });
            });

            $(".previous").click(function () {
                current_fs = $(this).parent();
                previous_fs = $(this).parent().prev();

                $("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");

                previous_fs.show();

                current_fs.animate({ opacity: 0 }, {
                    step: function (now) {
                        opacity = 1 - now;
                        current_fs.css({
                            'display': 'none',
                            'position': 'relative'
                        });
                        previous_fs.css({ 'opacity': opacity });
                    },
                    duration: 600
                });
            });

            $(".add-another").click(function () {
                var container = $(this).siblings('.work-experience-container, .education-item, .certification-item, .skills-container').last();
                var entryClone = container.clone().find('input').val('').end().find('textarea').val('').end();
                $(this).before(entryClone);
            });

            $(document).on('click', '.delete-btn', function () {
                $(this).parent().remove();
            });
        });

        document.addEventListener('DOMContentLoaded', function() {
        var dobInput = document.getElementById('dateofbirth');
        dobInput.type = 'text'; // Start with type text
        dobInput.addEventListener('focus', function() {
            this.type = 'date';
        });
        dobInput.addEventListener('blur', function() {
            if (!this.value) this.type = 'text';
        });
    });

        $(document).ready(function () {
            var currentYear = new Date().getFullYear(); 

            $("#dateofbirth").datepicker({
                dateFormat: "mm/dd/yy",
                changeMonth: true,
                changeYear: true,
                yearRange: "1900:" + currentYear
            });
        });

        document.addEventListener('DOMContentLoaded', function () {
    const addAnotherButton = document.querySelector('.add-another');
    const experienceList = document.getElementById('experience-list');

    function updateExperiencePreview() {
        // Clear previous entries
        experienceList.innerHTML = '';

        // Get all work experience entries
        const workExperienceEntries = document.querySelectorAll('.work-experience-entry');

        workExperienceEntries.forEach(entry => {
            const company = entry.querySelector('input[name="company[]"]').value.trim();
            const role = entry.querySelector('input[name="role[]"]').value.trim();
            const tenure = entry.querySelector('input[name="tenure[]"]').value.trim();
            const responsibilities = entry.querySelector('textarea[name="responsibilities[]"]').value.trim().split('\n');

            // Create a new experience block
            const experienceBlock = document.createElement('div');
            const experienceHTML = `
                <h3>${company}</h3>
                <h4><span>${role}</span> <span>${tenure}</span></h4>
                <ul>
                    ${responsibilities.map(item => `<li>${item}</li>`).join('')}
                </ul>
            `;
            experienceBlock.innerHTML = experienceHTML;
            experienceList.appendChild(experienceBlock);
        });
    }

    // Listen for changes in the work experience fields
    document.querySelectorAll('.work-experience-entry input, .work-experience-entry textarea').forEach(input => {
        input.addEventListener('input', updateExperiencePreview);
    });

    // Also update the preview when a new entry is added
    addAnotherButton.addEventListener('click', function () {
        setTimeout(() => {
            document.querySelectorAll('.work-experience-entry input, .work-experience-entry textarea').forEach(input => {
                input.removeEventListener('input', updateExperiencePreview); // Avoid multiple bindings
                input.addEventListener('input', updateExperiencePreview);
            });
            updateExperiencePreview(); // Update preview immediately after adding a new entry
        }, 100); // Short delay to ensure the new entry is added
    });

    $(document).on('click', '.delete-btn', function () {
        $(this).parent().remove();
        updateEducationPreview();
    });
    // Initialize preview with any existing data
    updateExperiencePreview();
});

document.addEventListener('DOMContentLoaded', function () {
    const addAnotherEducationButton = document.querySelector('#education .add-another');
    const educationList = document.getElementById('education-list');

    function updateEducationPreview() {
        // Clear previous entries
        educationList.innerHTML = '';

        // Get all education entries
        const educationEntries = document.querySelectorAll('.education-item');

        educationEntries.forEach(entry => {
            const school = entry.querySelector('input[name="school[]"]').value.trim();
            const qualification = entry.querySelector('input[name="qualification[]"]').value.trim();
            const tenure = entry.querySelector('input[name="tenure[]"]').value.trim();

            // Create a new education block
            const educationBlock = document.createElement('div');
            const educationHTML = `
                <h3>${school}</h3>
                <h4>${qualification} <span>${tenure}</span></h4>
            `;
            educationBlock.innerHTML = educationHTML;
            educationList.appendChild(educationBlock);
        });
    }

    function attachInputListeners() {
        document.querySelectorAll('.education-item input').forEach(input => {
            input.removeEventListener('input', updateEducationPreview); // Avoid multiple bindings
            input.addEventListener('input', updateEducationPreview);
        });
    }

    // Listen for changes in the education fields
    attachInputListeners();

    // Update the preview when a new education entry is added
    addAnotherEducationButton.addEventListener('click', function () {
        setTimeout(() => {
            attachInputListeners();
            updateEducationPreview(); // Update preview immediately after adding a new entry
        }, 100); // Short delay to ensure the new entry is added
    });

    // Listen for delete button clicks
    $(document).on('click', '.delete-btn', function () {
        $(this).parent().remove();
        updateEducationPreview();
    });

    // Initialize preview with any existing data
    updateEducationPreview();
});

document.addEventListener('DOMContentLoaded', function() {
    const addAnotherSkillButton = document.querySelector('#skills-languages .add-another');
    const skillsList = document.getElementById('skills-list'); // Make sure you have an element with this ID in your HTML where you want to display the skills

    function updateSkillsPreview() {
        // Clear previous entries
        skillsList.innerHTML = '';

        // Get all skill entries
        const skillEntries = document.querySelectorAll('.skills-container input[name="skill[]"]');

        skillEntries.forEach(entry => {
            const skill = entry.value.trim();

            // Create a new skill block, assuming you want each skill to be shown as a list item
            const skillItem = document.createElement('li');
            skillItem.textContent = skill;
            skillsList.appendChild(skillItem);
        });
    }

    function attachSkillInputListeners() {
        document.querySelectorAll('.skills-container input').forEach(input => {
            input.removeEventListener('input', updateSkillsPreview); // Avoid multiple bindings
            input.addEventListener('input', updateSkillsPreview);
        });
    }

    // Listen for changes in the skills fields
    attachSkillInputListeners();

    // Update the preview when a new skill entry is added
    addAnotherSkillButton.addEventListener('click', function() {
        setTimeout(() => {
            attachSkillInputListeners();
            updateSkillsPreview(); // Update preview immediately after adding a new entry
        }, 100); // Short delay to ensure the new entry is added
    });

    // Listen for delete button clicks
    $(document).on('click', '.delete-btn', function() {
        $(this).parent().remove();
        updateSkillsPreview();
    });

    // Initialize preview with any existing data
    updateSkillsPreview();
});


document.addEventListener('DOMContentLoaded', function() {
    const progressSteps = document.querySelectorAll('#progressbar li');
    const fieldsets = document.querySelectorAll('fieldset');

    function navigateToStep(clickedIndex) {
        // Remove 'active' class from all steps and hide all fieldsets
        progressSteps.forEach((step, index) => {
            step.classList.remove('active');
            fieldsets[index].style.display = 'none';
        });

        // Add 'active' class back to the clicked step and all previous steps
        for (let i = 0; i <= clickedIndex; i++) {
            progressSteps[i].classList.add('active');
        }

        // Show the corresponding fieldset
        fieldsets[clickedIndex].style.display = 'block';
    }

    // Attach click event listeners to each step in the progress bar
    progressSteps.forEach((step, index) => {
        step.addEventListener('click', () => {
            navigateToStep(index);
        });
    });

    // Existing functionality for next and previous buttons
    $(".next").click(function() {
        let current_fs = $(this).parent();
        let next_fs = $(this).parent().next();
        let currentStepIndex = $("fieldset").index(current_fs);

        // Activate the next step on the progressbar
        $("#progressbar li").eq(currentStepIndex + 1).addClass('active');

        // Show the next fieldset
        next_fs.show();
        // Hide the current fieldset with style
        current_fs.animate({opacity: 0}, {
            step: function(now, mx) {
                // As the opacity of current_fs reduces to 0 - stored in "now"
                // 1. Scale current_fs down to 80%
                // 2. Bring next_fs from the right(50%)
                let scale = 1 - (1 - now) * 0.2;
                let left = (now * 50) + "%";
                let opacity = 1 - now;
                current_fs.css({
                    'transform': 'scale(' + scale + ')',
                    'position': 'absolute'
                });
                next_fs.css({'left': left, 'opacity': opacity});
            },
            duration: 800,
            complete: function() {
                current_fs.hide();
                current_fs.css('position', 'relative'); // Reset position to avoid CSS conflict with direct clicks
            }
        });
    });

    $(".previous").click(function() {
        let current_fs = $(this).parent();
        let previous_fs = $(this).parent().prev();
        let currentStepIndex = $("fieldset").index(current_fs);

        // De-activate the current step and activate the previous step on the progressbar
        $("#progressbar li").eq(currentStepIndex).removeClass('active');

        // Show the previous fieldset
        previous_fs.show();
        // Hide the current fieldset with style
        current_fs.animate({opacity: 0}, {
            step: function(now, mx) {
                // As the opacity of current_fs reduces to 0 - stored in "now"
                // 1. Scale previous_fs from 80% to 100%
                // 2. Take current_fs to the right(50%) - from 0%
                let scale = 0.8 + (1 - now) * 0.2;
                let left = ((1 - now) * 50) + "%";
                let opacity = 1 - now;
                current_fs.css({'left': left});
                previous_fs.css({'transform': 'scale(' + scale + ')', 'opacity': opacity});
            },
            duration: 800,
            complete: function() {
                current_fs.hide();
                current_fs.css('position', 'relative'); // Reset position to avoid CSS conflict with direct clicks
            }
        });
    });
});


const fileInput = document.getElementById('profile-upload');
    const fileNameDisplay = document.querySelector('.file-name');

    fileInput.addEventListener('change', function() {
        const fileName = this.files.length > 0 ? this.files[0].name : 'No file chosen...';
        fileNameDisplay.textContent = fileName;
    });

    document.querySelector('.file-upload-button').addEventListener('click', function() {
        fileInput.click();
    });

    document.addEventListener('DOMContentLoaded', function() {
    const addAnotherReferencesButton = document.querySelector('#references .add-another');

    // Function to add a new reference entry dynamically
    function addReference() {
        const container = document.querySelector('#references'); // Container for reference entries
        const originalEntry = container.querySelector('.referees-item');
        const newEntry = originalEntry.cloneNode(true); // Clone the first reference item

        // Clear the values in the cloned inputs
        newEntry.querySelectorAll('input').forEach(input => {
            input.value = '';
        });

        // Attach event to the new delete button in the cloned entry
        newEntry.querySelector('.delete-btn').addEventListener('click', function() {
            this.parentElement.remove();
            updateReferencesPreview(); // Update the list display after an entry is removed
        });

        container.insertBefore(newEntry, addAnotherReferencesButton); // Insert the new entry before the "Add Another" button
    }

    // Attach the addReference function to the "Add Another" button
    addAnotherReferencesButton.addEventListener('click', function() {
        addReference();
        updateReferencesPreview(); // Update the list display after adding a new entry
    });

    // Function to update the references list display
    function updateReferencesPreview() {
        const referencesList = document.getElementById('References-list');
        referencesList.innerHTML = ''; // Clear current list

        // Query all current entries and add them to the preview list
        const allEntries = document.querySelectorAll('.referees-item');
        allEntries.forEach((entry, index) => {
            const referee = entry.querySelector('input[name="Referees[]"]').value.trim();
            const company = entry.querySelector('input[name="Company[]"]').value.trim();
            const contact = entry.querySelector('input[name="contact[]"]').value.trim();

            if (referee && company && contact) { // Only add entries with all fields filled
                const listItem = document.createElement('li');
                listItem.textContent = `${referee} from ${company} - Contact: ${contact}`;
                referencesList.appendChild(listItem);
            }
        });
    }

    // Initial display update
    updateReferencesPreview();

    // Ensure delete buttons in existing entries are functional
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.remove();
            updateReferencesPreview();
        });
    });
});

// end of manipulation js

// index js
