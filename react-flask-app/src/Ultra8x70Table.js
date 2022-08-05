import axios from 'axios';
import React, { useMemo, useEffect, useState, useRef } from 'react';
import { toCurrency } from './helpers';
import Table from './components/Table';

function App() {

  let gpuPrice = 499.0
  let numGPU = 8
  let serverCost = 400.0
  

  const [price, setPrice] = useState(gpuPrice)
  const [serverP, setServerP] = useState(serverCost)
  const priceRef = useRef()
  const rigRef = useRef()

  function calcPrice() {
    let rigP = price*numGPU
    rigP+=parseFloat(serverP)
    console.log(typeof(rigP))
    return rigP
  }

  async function handlePriceChange(e) {
      const p = priceRef.current.value
      priceRef.current.value = null
      await axios("/api/data/gpu/3070/"+p)
      const result = await axios("/api/data/rig")
      console.log(result.data)
      setData(result.data)
      setPrice(p)
  }

  async function resetPrice(e) {
      await axios("/api/data/gpu/3070/"+gpuPrice)
      const result = await axios("/api/data/rig")
      setData(result.data)
      setPrice(gpuPrice)
  }

  async function handleRigPriceChange(e) {
    const p = rigRef.current.value
    rigRef.current.value = null
    await axios("/api/data/rig/3070/"+p)
    const result = await axios("/api/data/rig")
    console.log(result.data)
    setData(result.data)
    setServerP(p)
    
}

async function resetRigPrice(e) {
    await axios("/api/data/rig/3070/"+serverCost)
    const result = await axios("/api/data/rig")
    setData(result.data)
    setServerP(serverCost)
}

  // data state to store the API data. Its initial value is an empty array
  const [data, setData] = useState([]);

  // Using useEffect to call the API once mounted and set the data
  useEffect(() => {
    (async () => {
      const result = await axios("/api/data/rig");
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
            Header: "Ultra8x70",
            accessor: "Header"
          },
          {
            Header: "Ethereum",
            accessor: "gpu.3070.Ethereum"
          },
          {
            Header: "Conflux",
            accessor: "gpu.3070.Conflux"
          },
          {
            Header: "Ravencoin",
            accessor: "gpu.3070.Ravencoin"
          },
          {
            Header: "Bitcoin Gold",
            accessor: "gpu.3070.Bitcoin Gold"
          },
          {
            Header: "Ethereum Classic",
            accessor: "gpu.3070.Ethereum Classic"
          },
          {
            Header: "Flux",
            accessor: "gpu.3070.Flux"
          },
          {
            Header: "Ergo",
            accessor: "gpu.3070.Ergo"
          },
        ]
      },
    ],
    []
  );

  

  return (
    <>
      <div>
        <div>GPU Price: ${toCurrency(price)} x 8</div>
        <input ref={priceRef} type="number"/>
        <button onClick={handlePriceChange}>Change Price</button>
        <button onClick={resetPrice}>Reset</button>
        <div>Server Price: ${toCurrency(serverP)}</div>
        <input ref={rigRef} type="number"/>
        <button onClick={handleRigPriceChange}>Change Price</button>
        <button onClick={resetRigPrice}>Reset</button>
        <div>Rig Price: ${toCurrency(calcPrice())}</div>
      </div>
      <div className="App">
        <Table columns={columns} data={data} />
      </div>
    </>
  );
}

export default App;