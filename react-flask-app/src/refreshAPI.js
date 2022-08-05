import axios from 'axios';
import React, { useMemo, useEffect, useState } from 'react';
import { toCurrency } from './helpers';
import Table from './components/Table';

function App() {

  // data state to store the TV Maze API data. Its initial value is an empty array
  const [data, setData] = useState([]);

  // Using useEffect to call the API once mounted and set the data
  useEffect(() => {
    const interval = setInterval(() => {
        console.log("update")
        updateData()
    }, 10000)
  }, []);

  async function updateData() {
    await axios("/api/refresh")
    const result = await axios("/api/data/coin");
    setData(result.data);
    console.log(result.data)
  }



  return (
    <>
      <div id="refreshAPI">
        <button onClick={updateData}>Fetch Price</button>
      </div>
    </>
  );
}

export default App;