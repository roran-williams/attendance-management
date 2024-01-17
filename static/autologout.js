document.addEventListener("DOMContentLoaded", function() {
    // Set the timeout duration (in milliseconds)
    var timeoutDuration = 60000; // 1 minute = 60,000 milliseconds

    // Define the function to perform the logout
    function logoutUser() {
        window.location.href = "/logout"; // Redirect to the logout route
    }

    // Set a timeout to trigger the logout after the specified duration
    var timeout = setTimeout(logoutUser, timeoutDuration);

    // Reset the timeout if there's any user interaction
    document.addEventListener("mousemove", function() {
        clearTimeout(timeout);
        timeout = setTimeout(logoutUser, timeoutDuration);
    });
});

