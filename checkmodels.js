const mongoose = require('mongoose');
const dbi = 'mongodb+srv://Atul1603:Atuldubey@pdftoaudio.8pkov.mongodb.net/UserDataBase?retryWrites=true&w=majority&appName=PdfToAudio';

mongoose.connect(dbi)
  .then(() => {
    console.log("Connected to MongoDB");
  })
  .catch((err) => {
    console.log("An error occurred:", err);
  });
