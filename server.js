const express = require('express');
const path = require('path');
const mongoose = require('mongoose');
const bcrypt = require('bcrypt'); // For hashing passwords
const fetch = require('node-fetch'); 
const app = express();

// Middleware to parse form data
app.use(express.urlencoded({ extended: true }));
app.use(express.json()); // For parsing JSON data in chatbot requests

// Serve static files
app.use('/css', express.static(path.join(__dirname, 'css')));
app.use('/static', express.static(path.join(__dirname, 'static')));

// Serve main.html as the default page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'main.html')); // Serve main.html by default
});

// Routes for all pages
app.get('/templates/main.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'main.html')); // Serve main.html
});

app.get('/templates/aboutus.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'aboutus.html')); // Serve aboutus.html
});

app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'login.html')); // Serve login.html
});

app.get('/signup', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'signup.html')); // Serve signup.html
});


// MongoDB Connection Setup
const dbURI = 'mongodb+srv://Atul1603:Atuldubey@pdftoaudio.8pkov.mongodb.net/UserDataBase?retryWrites=true&w=majority&appName=PdfToAudio';
mongoose
     .connect(dbURI)
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.error('Failed to connect to MongoDB:', err));

// Define User Schema and Model
const userSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    password: { type: String, required: true },
});

const User = mongoose.model('User', userSchema);

// Handle signup form submission (POST)
app.post('/signup', async (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ error: 'All fields are required.' });
    }

    try {
        const existingUser = await User.findOne({ username });
        if (existingUser) {
            return res.status(409).json({ error: 'Username already exists.' });
        }

        // Hash the password before saving
        const hashedPassword = await bcrypt.hash(password, 10);
        const newUser = new User({ username, password: hashedPassword });
        await newUser.save();

        console.log(`New user registered: ${username}`);
        res.status(201).json({ success: true, message: 'User registered successfully.' });
    } catch (error) {
        console.error('Error saving user:', error.message);
        res.status(500).json({ error: 'Internal server error.' });
    }
});

// Handle login form submission (POST)
app.post('/login', async (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ error: 'All fields are required.' });
    }

    try {
        const user = await User.findOne({ username });
        if (user && (await bcrypt.compare(password, user.password))) {
            res.status(200).json({ success: true, redirect: 'http://127.0.0.1:5000/' });
        } else {
            res.status(401).json({ error: 'Invalid credentials.' });
        }
    } catch (error) {
        console.error('Error during login:', error.message);
        res.status(500).json({ error: 'Internal server error.' });
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