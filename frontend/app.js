const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();

const API_URL = process.env.API_URL || "http://localhost:8000";
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));

app.get('/health', (req, res) => {
  res.status(200).send('OK');
});

app.post('/submit', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`, {}, { timeout: 5000 });
    res.json(response.data);
  } catch (err) {
    console.error("Error creating job:", err.message);
    res.status(500).json({ error: "something went wrong" });
  }
});

app.get('/status/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`, { timeout: 5000 });
    res.json(response.data);
  } catch (err) {
    console.error(`Error fetching status for job ${req.params.id}:`, err.message);
    res.status(500).json({ error: "something went wrong" });
  }
});

app.listen(PORT, () => {
  console.log(`Frontend running on port ${PORT}`);
});
