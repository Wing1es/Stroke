import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import bodyParser from 'body-parser';
import { spawn } from 'child_process';
import ejs from 'ejs';

const app = express();
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);


app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static("./public"));


app.set('view engine', 'ejs');

function trainModel() {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python3', ['models/model.py']);

        pythonProcess.stdout.on('data', (data) => {
            console.log(`Model.py output: ${data}`);
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`Model.py error: ${data}`);
        });

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                console.log('Model training completed successfully.');
                resolve();
            } else {
                reject(new Error(`Model training failed with exit code ${code}`));
            }
        });
    });
}

function fillUp(value, length) {
    const arr = new Array(length).fill(0);
    if (value >= 0 && value < length) arr[value] = 1;
    return arr;
}

// Routes
app.get('/', (req, res) => {
    res.render("index");
});

app.get('/about', (req, res) => {
    res.render("about");
});

app.post('/', (req, res) => {
    const pythonProcess = spawn('python3', ['models/predict.py']);

    const gender = fillUp(parseInt(req.body.gen), 2);
    const residence = fillUp(parseInt(req.body.resd), 2);
    const married = fillUp(parseInt(req.body.marry), 2);
    const workType = fillUp(parseInt(req.body.work), 5);
    const smokingStatus = fillUp(parseInt(req.body.smoke), 3);

    const inputData = {
        'age': parseFloat(req.body.age),
        'hypertension': parseInt(req.body.hyper),
        'heart_disease': parseInt(req.body.heart),
        'avg_glucose_level': parseFloat(req.body.avgg),
        'bmi': parseFloat(req.body.bmi),
        'Rural': residence[0],
        'Urban': residence[1],
        'Male': gender[1],
        'Female': gender[0],
        'Yes': married[1],
        'No': married[0],
        'Private': workType[0],
        'Self_employed': workType[1],
        'children': workType[2],
        'Govt_job': workType[3],
        'Never_worked': workType[4],
        'formerly_smoked': smokingStatus[0],
        'never_smoked': smokingStatus[1],
        'smokes': smokingStatus[2]
    };

    pythonProcess.stdin.write(JSON.stringify(inputData));
    pythonProcess.stdin.end();

    let output = '';

    pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        if (code === 0) {
            try {
                const parsedOutput = JSON.parse(output.trim()); 
                res.render('success', { result: parsedOutput }); 
            } catch (error) {
                console.error('Error parsing Python output:', error);
                res.render('failure');
            }
        } else {
            console.error(`Python process exited with code: ${code}`);
            res.render('failure');
        }
    });
});

// Train model and Start the server
trainModel()
    .then(() => {
        const PORT = process.env.PORT || 3000;
        app.listen(PORT, () => {
            console.log(`Server running on port ${PORT}`);
        });
    })
    .catch((err) => {
        console.error('Failed to train the model:', err);
        process.exit(1);
    });
