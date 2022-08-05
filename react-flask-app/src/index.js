import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import CoinTable from './CoinTable';
import GPUTable from './GPUTable'
import Ultra8x70TTable from './Ultra8x70TTable'
import Ultra8x70Table from './Ultra8x70Table'
import Ultra8x60TTable from './Ultra8x60TTable'
import Ultra8x60Table from './Ultra8x60Table'
import reportWebVitals from './reportWebVitals';
import refreshAPI from './refreshAPI'

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <CoinTable />
  </React.StrictMode>
);

const gpu = ReactDOM.createRoot(document.getElementById('gpu'));
gpu.render(
  <React.StrictMode>
    <GPUTable />
  </React.StrictMode>
);

const u70t = ReactDOM.createRoot(document.getElementById('u70t'));
u70t.render(
  <React.StrictMode>
    <Ultra8x70TTable />
  </React.StrictMode>
);

const u70 = ReactDOM.createRoot(document.getElementById('u70'));
u70.render(
  <React.StrictMode>
    <Ultra8x70Table />
  </React.StrictMode>
);

const u60t = ReactDOM.createRoot(document.getElementById('u60t'));
u60t.render(
  <React.StrictMode>
    <Ultra8x60TTable />
  </React.StrictMode>
);

const u60 = ReactDOM.createRoot(document.getElementById('u60'));
u60.render(
  <React.StrictMode>
    <Ultra8x60Table />
  </React.StrictMode>
);

const refresh = ReactDOM.createRoot(document.getElementById('refreshAPI'))
refresh.render(
  <React.StrictMode>
    <refreshAPI />
  </React.StrictMode>
)
// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
