document.getElementById('sendBtn').addEventListener('click', async () => {
  const link = document.getElementById('linkInput').value;
  const responseDiv = document.getElementById('response');
  responseDiv.textContent = 'Checking...';

  try {
    // Replace with your backend URL
    const res = await fetch('https://your-backend-url.com/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ link })
    });
    const data = await res.json();
    responseDiv.textContent = data.result || 'No result';
  } catch (err) {
    responseDiv.textContent = 'Error: ' + err.message;
  }
});