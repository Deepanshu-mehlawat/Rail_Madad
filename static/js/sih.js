document.addEventListener('DOMContentLoaded', function() {
    const typeSelect = document.getElementById('type');
    const subTypeSelect = document.getElementById('subType');
    const imageUpload = document.getElementById('imageUpload');
    const imagePreview = document.getElementById('imagePreview');
    let categories;

    // Fetch the categories from the JSON file
    fetch('/static/categories.json')
        .then(response => response.json())
        .then(data => {
            categories = data;
            populateTypes();
        })
        .catch(error => console.error('Error loading categories:', error));

    function populateTypes() {
        typeSelect.innerHTML = '<option value="">Select Type</option>';
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.type;
            option.textContent = category.type;
            typeSelect.appendChild(option);
        });
    }

    typeSelect.addEventListener('change', function() {
        const selectedCategory = categories.find(cat => cat.type === this.value);
        populateSubTypes(selectedCategory ? selectedCategory.subtype : []);
    });

    function populateSubTypes(subtypes) {
        subTypeSelect.innerHTML = '<option value="">Select Sub Type</option>';
        subtypes.forEach(subtype => {
            const option = document.createElement('option');
            option.value = subtype;
            option.textContent = subtype;
            subTypeSelect.appendChild(option);
        });
        subTypeSelect.disabled = subtypes.length === 0;
    }

    // Image upload preview
    imageUpload.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                imagePreview.innerHTML = '';
                imagePreview.appendChild(img);
            }
            reader.readAsDataURL(file);
        } else {
            imagePreview.innerHTML = '';
        }
    });

    document.getElementById('complaintForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Create FormData object
        const formData = new FormData(this);
        
        // Add additional form data
        formData.append('type', typeSelect.value);
        formData.append('subType', subTypeSelect.value);
        
        // Here you would typically send the formData to your server
        // For demonstration, we'll just log it
        for (let [key, value] of formData.entries()) {
            console.log(key, value);
        }
        
        // In a real application, you'd use fetch or XMLHttpRequest to send the data
        // For example:
        /*
        fetch('/submit-complaint', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // Handle success (e.g., show a success message, reset form)
        })
        .catch((error) => {
            console.error('Error:', error);
            // Handle error (e.g., show an error message)
        });
        */
    });
});