import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Load resume data
const loadResumeData = () => {
  try {
    const filePath = path.join(__dirname, '../../data/resume.yaml');
    const fileContents = fs.readFileSync(filePath, 'utf8');
    return yaml.load(fileContents);
  } catch (error) {
    console.error('Error loading resume data:', error);
    return null;
  }
};

// API endpoint to get resume data
app.get('/api/resume', (req, res) => {
  const resumeData = loadResumeData();
  if (resumeData) {
    res.json(resumeData);
  } else {
    res.status(500).json({ error: 'Failed to load resume data' });
  }
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK' });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});