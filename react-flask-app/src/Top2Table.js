import axios from 'axios';
import React, { useMemo, useEffect, useState, useRef } from 'react';
import { toCurrency } from './helpers';
import Table from './components/Table';

function App() {

  let gpuPrice = 499.0
  let numGPU = 8
  let serverCost = 400.0
  let numRigs = 1000
  

  const [price, setPrice] = useState(gpuPrice)
  const [serverP, setServerP] = useState(serverCost)
  const [rigs, setRigs] = useState(numRigs)
  const priceRef = useRef()
  const rigsRef = useRef()

  function calcPrice() {
    let rigP = price*numGPU
    rigP+=parseFloat(serverP)
    console.log(typeof(rigP))
    return rigP
  }

  async function handleRigsChange(e) {
    const r = rigsRef.current.value
    rigsRef.current.value = null
    const result = await axios("/api/data/rig/best/"+r)
    console.log(result.data)
    setData(result.data)
    setRigs(r)
}

async function resetRigs(e) {
    rigsRef.current.value = null
    const result = await axios("/api/data/rig/best")
    setData(result.data)
    setRigs(numRigs)
}

  // data state to store the API data. Its initial value is an empty array
  const [data, setData] = useState([]);

  let n1 = ""
  let n2 = ""

  // Using useEffect to call the API once mounted and set the data
  useEffect(() => {
    (async () => {
      const result = await axios("/api/data/rig/best");
      setData(result.data);
      console.log(result.data)
    })();
  }, []);

  /* 
    - Columns is a simple array right now, but it will contain some logic later on. It is recommended by react-table to memoize the columns data
    - Here in this example, we have grouped our columns into two headers. react-table is flexible enough to create grouped table headers
  */

  const columns = useMemo(
    () => [
      {
        // first group - TV Show
        Header: " ",
        // First group columns
        columns: [
          {
            Header: " ",
            accessor: "Header"
          },
          {
            Header: "Number 1",
            accessor: "no1"
          },
          {
            Header: "Number 2",
            accessor: "no2"
          },
          {
            Header: "Total",
            accessor: "total"
          },
        ]
      },
    ],
    []
  );

  

  return (
    <>
      <div># of Rigs: {rigs}</div>
        <input ref={rigsRef} type="number"/>
        <button onClick={handleRigsChange}>Change # of Rigs</button>
        <button onClick={resetRigs}>Reset</button>
      <div className="App">
        <Table columns={columns} data={data} />
      </div>
    </>
  );
}

export default App;