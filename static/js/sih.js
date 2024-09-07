document.getElementById("complaintButton").addEventListener("click", function() {
    document.getElementById("complaints").scrollIntoView({behavior: "smooth"});
});

document.getElementById("complaintForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const category = document.getElementById("category").value;
    const message = document.getElementById("message").value;

    alert(`Thank you ${name}, your complaint about ${category} has been received. We will contact you at ${email} soon.`);

    document.getElementById("complaintForm").reset();
});
