
(() => {
  document.querySelector('#token').value = location.hash.substr(1);
})()


const fnSubmit = (e) => {
  const formData = new FormData(e.target);
  const data = {};
  const mask = document.querySelector('#mask');

  for(let [key, value] of formData)
    data[key] = value;

  if(data.new_pwd !== data.new_pwd2)
    console.log('exception of no match');
  else if(sumStrongPassword(data.new_pwd) < 0.6)
    console.log('bad reputation of password');
  else {
    mask.classList.add('mask-show');
    fetch('/change-password-with-token', {
      method: 'POST',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(res => res.json())
      .then(data => {
        alert(data.message);

        if(data.success) {
          if(location.hash === '#autoClose')
            window.close();
          else if(location.hash === '#noReset')
            console.log('foo()');
          else {
            e.target.reset();
            resetMatchPassword();
            resetStrongPassword();
          }
        }
      })
      .catch(err => {
        console.log(err);
        alert('Recurso indisponivel no momento.');
      })
      .finally(() => mask.classList.remove('mask-show'));
  }

  return false;
}

const strongTest = [
  // verifica tamanho
  value => {
    if(value.length < 6)
      return -9999.0;
    else if(value.length < 8)
      return 0.4;
    else if(value.length == 8)
      return 0.7;
    else
      return 1.0;
  },
  // verifica senhas faceis
  value => {
    const badPasswords = [
      '123mudar', 'q1w2e3r4t5', '123456',
      'Password', '12345678', 'qwerty', '12345', '123456789', 'letmein',
      '1234567', 'football', 'iloveyou', 'admin', 'welcome', 'monkey',
      'login', 'abc123', 'starwars', '123123', 'dragon', 'passw0rd',
      'master', 'hello', 'freedom', 'whatever', 'qazwsx', 'trustno1'
    ];

    return (badPasswords.indexOf(value) < 0 ? 0.5 : -9999.0);
  },
  // verifica repetidos seguidos
  value => {
    const chars = [];

    Array.from(value).forEach(
      c => {
        if(chars.indexOf(c) < 0)
          chars.push(c)
      }
    );

    return (chars.length / value.length);
  },
  // verifica letras e números
  value => {
    const lower = /[a-z]/;
    const upper = /[A-Z]/;
    const numbers = /[0-9]/;
    const special = /(!|@|#|\$|%|&|\*|\_|\+)/;

    let reputation = 0;

    if(lower.test(value))
      reputation += 0.2;

    if(upper.test(value))
      reputation += 0.2;

    if(numbers.test(value))
      reputation += 0.2;

    if(special.test(value))
      reputation += 0.4;

    return reputation;
  },
  // verifica sequencias faceis
  value => {
    const badSequences = [
      '123', '456', '789', 'adm', 'qwert',
      'asdf', 'abc', '@#$%'
    ];

    let flag = false;
    badSequences.forEach(badSequence => {
      if(!flag && value.indexOf(badSequence) >= 0)
        flag = true;
    });

    return (!flag ? 1.0 : -9999.0);
  }
]

const sumStrongPassword = (value) => {
  const testData = strongTest.map(test => test(value));
  const sum = testData.reduce((a, b) => a + b);
  const reputation = ((sum >= 0.0 ? sum : 0.0) / strongTest.length);

  return reputation;
}

const resetStrongPassword = () => {
  const el = document.querySelector('#strongOutput');

  el.innerHTML = 'Força';
  el.className = "";
}

const resetMatchPassword = () => {
  const el = document.querySelector('#matchOutput');

  el.innerHTML = 'Avaliação';
  el.className = "";
}

const fnSumStrongPassword = (e) => {
  const reputation = sumStrongPassword(e.target.value);
  const el = document.querySelector('#strongOutput');

  if(e.target.value === "")
    resetStrongPassword();
  else if(reputation > 0.7) {
    el.innerHTML = 'Forte';
    el.className = 'good';
  } else if(reputation > 0.6 && reputation < 0.7) {
    el.innerHTML = 'Moderado';
    el.className = 'regular';
  } else if(reputation > 0.4 && reputation < 0.6) {
    el.innerHTML = 'Fraco';
    el.className = 'ugly';
  } else {
    el.innerHTML = 'Conhecido';
    el.className = 'bad';
  }
}

const fnMatchPassword = (e) => {
  const value = e.target.value;
  const base = document.querySelector('#new_pwd').value;
  const el = document.querySelector('#matchOutput');

  if(value === "" || base === "")
    resetMatchPassword();
  else if(value === base) {
    el.innerHTML = 'Igual';
    el.className = 'good';
  } else {
    el.innerHTML = 'Diferente';
    el.className = 'bad';
  }
}
