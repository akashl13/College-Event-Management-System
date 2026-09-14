window.addEventListener('load', () => {
  if (!window.Html5Qrcode) return;
  const reader = new Html5Qrcode('reader');
  reader.start({ facingMode: 'environment' }, { fps: 10, qrbox: 220 }, value => {
    const match = value.match(/\/verify\/([^/?#]+)/);
    const code = match ? match[1] : value;
    document.querySelector('#registration-code').value = code;
    document.querySelector('#attendance-form').requestSubmit();
    reader.stop();
  }, () => {}).catch(() => {});
});