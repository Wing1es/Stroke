import express from 'express';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import bodyParser from 'body-parser';
import { spawn } from 'child_process';
import ejs from 'ejs';

const app = express();
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Middleware setup
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static("./public"));

// Set EJS as the view engine
app.set('view engine', 'ejs');

// Routes
app.get('/', (req, res) => {
    res.render("index");
});

app.get('/about', (req, res) => {
    res.render("about");
});

app.post('/', (req, res) => {
    const pythonProcess = spawn('python3', ['code.py']); // Ensure 'python3' is used for Python 3 compatibility

    const inputData = {
        'age': parseFloat(req.body.age),
        'gender': parseInt(req.body.gen),
        'ever_married': parseInt(req.body.marry),
        'Residence_type': parseInt(req.body.resd),
        'avg_glucose_level': parseFloat(req.body.avgg),
        'bmi': parseFloat(req.body.bmi),
        'work_type': parseInt(req.body.work),
        'smoking_status': parseInt(req.body.smoke),
    };

    // Send input data to the Python process
    pythonProcess.stdin.write(JSON.stringify(inputData));
    pythonProcess.stdin.end();

    let output = '';

    // Capture standard output from the Python process
    pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
    });

    // Capture errors from the Python process
    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python error: ${data}`);
    });

    // Handle the process completion
    pythonProcess.on('close', (code) => {
        if (code === 0) {
            try {
                const parsedOutput = JSON.parse(output.trim()); // Parse the JSON output
                res.render('success', { result: parsedOutput }); // Render success page with results
            } catch (error) {
                console.error('Error parsing Python output:', error);
                res.render('failure'); // Render failure page in case of parsing issues
            }
        } else {
            console.error(`Python process exited with code: ${code}`);
            res.render('failure'); // Render failure page for non-zero exit codes
        }
    });
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
