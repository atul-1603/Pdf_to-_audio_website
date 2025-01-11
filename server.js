const express = require('express');
const path = require('path');
const app = express();

// Middleware to parse form data
app.use(express.urlencoded({ extended: true }));

// Serve static files (e.g., CSS)
app.use('/css', express.static(path.join(__dirname, 'css')));

// Serve main.html as the default page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'main.html')); // Serve main.html by default
});

// Routes for all pages
app.get('/main.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'main.html')); // Serve main.html
});

app.get('/aboutus.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'aboutus.html')); // Serve aboutus.html
});

app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, 'login.html')); // Serve login.html
});

app.get('/signup', (req, res) => {
    res.sendFile(path.join(__dirname, 'signup.html')); // Serve signup.html
});

// Handle login form submission (POST)
app.post('/login', (req, res) => {
    const { username, password } = req.body;

    // Basic validation (use real validation logic in production)
    if (username && password) {
        // Simulate successful login
        // Redirect to Flask server's index.html
        res.redirect('http://127.0.0.1:5000/');
    } else {
        res.status(400).send('Invalid credentials. <a href="/login">Go back</a>.');
    }
});

// Handle signup form submission (POST)
app.post('/signup', (req, res) => {
    const { username, password } = req.body;

    // Basic validation
    if (username && password) {
        console.log(`New user registered: ${username}`);
        res.redirect('/login'); // Redirect to login after successful signup
    } else {
        res.status(400).send('All fields are required. <a href="/signup">Go back</a>.');
    }
});

// Catch-all route for undefined paths
app.use((req, res) => {
    res.status(404).send('Page not found. <a href="/">Go to Home</a>.');
});

// Start the Express server
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Express server is running on http://localhost:${PORT}`);
});
