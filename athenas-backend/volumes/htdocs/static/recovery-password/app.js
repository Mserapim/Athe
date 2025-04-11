
const fnSubmit = (e) => {
  const formData = new FormData(e.target);
  const data = {};

  for(let [key, value] of formData)
    data[key] = value;

  const [bornYear, bornMonth, bornDay] = data.data_nascimento.split('-')
  const mask = document.querySelector('#mask');

  data.data_nascimento = [bornDay, bornMonth, bornYear].join('/');

  mask.classList.add('mask-show');
  fetch('/recovery-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(data => {
      const ouput = document.querySelector('#output');
      const form = document.querySelector('form');
      const text = output.innerHTML;

      if(data.success) {
        form.classList.add('display-none');
        output.classList.remove('display-none');
        setTimeout(() => output.classList.add('output-visible'), 1);
        output.innerHTML = text.replace('{{ email }}', data.email);
      } else {
        alert(data.message);
      }
    })
    .catch((err) => {
      console.log(err);
      alert('Recurso indisponivel no momento.');
    })
    .finally(() => mask.classList.remove('mask-show'));

  return false;
}
