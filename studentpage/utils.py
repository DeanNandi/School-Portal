import re

# Map full address names to their abbreviations
COURSE_CLASSES_DICT = dict(
    Online='ONL',
    Nairobi_CBD='CBD',
    Nairobi_Hospital='NBH',
    Nairobi_Karen='KHS',
    Nairobi_Daystar='DUS',
    Mombasa='MSA',
    Muranga='MRG',
    Kisumu='KSM',
    Kisii='KSI',
    Eldoret='ELD',
    Thika='THK',
    Nakuru='NKS',
)

# Create a regex pattern that matches any of the abbreviations
LOCATION_PATTERN = '|'.join(COURSE_CLASSES_DICT.values())


def update_admission_number(old_number):
    if not old_number:
        return old_number

    # Extract the parts of the old admission number
    match = re.match(rf'(\d{{2}})(\d{{2}})({LOCATION_PATTERN})(\d+)', old_number)
    if not match:
        return old_number  # Return unchanged if it doesn't match the expected format

    year, month, location, number = match.groups()

    # Remove leading zeros from the number part
    number = str(int(number))

    # Construct the new format
    new_number = f"{year}{month}{location}{number}"

    return new_number
