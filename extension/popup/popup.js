document.getElementById('sendBtn').addEventListener('click', async () => {
  const link = document.getElementById('linkInput').value;
  const responseDiv = document.getElementById('response');
  responseDiv.textContent = 'Checking...';

  try {
    const res = await fetch('http://127.0.0.1:5000/analiser', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_url: link })
    });
    const data = await res.json();
    responseDiv.textContent = data['resumo'] || 'No result';
  } catch (err) {
    responseDiv.textContent = 'Error: ' + err.message;
  }
});