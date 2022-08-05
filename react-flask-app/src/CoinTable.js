import axios from 'axios';
import React, { useMemo, useEffect, useState } from 'react';
import { toCurrency } from './helpers';
import Table from './components/Table';

function App() {

  // data state to store the TV Maze API data. Its initial value is an empty array
  const [data, setData] = useState([]);

  // Using useEffect to call the API once mounted and set the data
  useEffect(() => {
    (async () => {
      const result = await axios("/api/data/coin");
      setData(result.data);
      console.log(result.data)
    })();
  }, []);

  async function updateData() {
    await axios("/api/refresh")
    const result = await axios("/api/data/coin");
    setData(result.data);
    console.log(result.data)
  }

  /* 
    - Columns is a simple array right now, but it will contain some logic later on. It is recommended by react-table to memoize the columns data
    - Here in this example, we have grouped our columns into two headers. react-table is flexible enough to create grouped table headers
  */
  const columns = useMemo(
    () => [
      {
        // first group - TV Show
        Header: "Coins",
        // First group columns
        columns: [
          {
            Header: "Name",
            accessor: "Name"
          },
          {
            Header: "Symbol",
            accessor: "Symbol"
          },
          {
            Header: "Price",
            accessor: "Price",
            Cell: ({cell: {value}}) => {
              const val = toCurrency(value)
              return('$' + val)
            }
          },
        ]
      }
    ],
    []
  );

  

  return (
      <div className="CoinTable">
        <button onClick={updateData}>Fetch Prices</button>
        <Table columns={columns} data={data} />
      </div>
  );
}

export default App;