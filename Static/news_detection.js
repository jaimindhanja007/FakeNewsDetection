// Get the form elements
const inputMethod = document.getElementById('input-method');
const inputTextArea = document.getElementById('input-data');
const newsletterSelect = document.getElementById('select-newsletter');
const detectForm = document.querySelector('.detect form');

// Add event listener for form submission
detectForm.addEventListener('submit', (event) => {
  // Prevent default form submission
  event.preventDefault();

  // Get the input value and type
  const inputValue = inputTextArea.value.trim();
  const inputType = inputMethod.value;

  // Check if the input value is empty
  if (inputValue === '') {
    alert('Please enter a valid input');
    return;
  }

  // If the input type is URL, validate the URL
  if (inputType === 'url') {
    const urlRegex = /^(ftp|http|https):\/\/[^ "]+$/;

    if (!urlRegex.test(inputValue)) {
      alert('Please enter a valid URL');
      return;
    }

    // Check if the newsletter option matches the URL domain
    const urlDomain = new URL(inputValue).hostname.split('.');
    const present = urlDomain.includes(newsletterSelect.value.toLowerCase());
    if (!(present)) {
        console.log(urlDomain);
        console.log(newsletterSelect.value.toLowerCase());
        alert('Please select the correct newsletter');
      return;
    }
  }

  // If the input type is text, check the minimum number of characters
  if (inputType === 'text') {
    if (inputValue.length < 600) {
      alert('Please enter at least 600 characters');
      return;
    }
  }

  // If all checks pass, submit the form
  detectForm.submit();
});
