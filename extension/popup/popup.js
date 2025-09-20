document.getElementById('sendBtn').addEventListener('click', async () => {
  const link = document.getElementById('linkInput').value;
  const responseDiv = document.getElementById('response');
  responseDiv.textContent = 'Verificando vídeo...';

  try {
    const res = await fetch('http://127.0.0.1:5000/analiser', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_url: link })
    });
    const data = await res.json();

    const testoFormatado = `
    <b>Potencialmente FakeNews?</b>${data['potencial_fake_news'] ? '<span class="highlight-yes">SIM!</span>' : '<span class="highlight-no">NÃO!</span>'}
    <b>Confiança:</b>${data['pontuacao_confianca']*100}%
    <b>Análise de Fontes:</b>${data['analise_fontes']}
    <b>Análise de Linguagem:</b>${data['analise_linguagem']}
    <b>Análise do Viés:</b>${data['analise_vies']}
    <b>Resumo Geral:</b>${data['resumo']}
    `;


    responseDiv.innerHTML = testoFormatado || 'Sem Resultado';
  } catch (err) {
    responseDiv.textContent = 'Error: ' + err.message;
  }
});
