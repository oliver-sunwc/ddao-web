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
      const result = await axios("/api/data/gpu");
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
        Header: "GPU",
        // First group columns
        columns: [
          {
            Header: "Name",
            accessor: "Name"
          },
        ]
      },
      {
        Header: "Coins",
        columns: [
          {
            Header: "Ethereum",
            accessor: "Data.Ethereum.24hUSD",
            Cell: ({cell: {value}}) => {
              const val = toCurrency(value)
              return('$' + val)
            }
          },
          {
            Header: "Conflux",
            accessor: "Data.Conflux.24hUSD",
            Cell: ({cell: {value}}) => {
              const val = toCurrency(value)
              return('$' + val)
            }
          },
          {
            Header: "Ravencoin",
            accessor: "Data.Ravencoin.24hUSD",
            Cell: ({cell: {value}}) => {
              const val = toCurrency(value)
              return('$' + val)
            }
          },
          {
            Header: "Bitcoin Gold",
            accessor: "Data.Bitcoin Gold.24hUSD",
            Cell: ({cell: {value}}) => {
              const val = toCurrency(value)
              return('$' + val)
            }

          },
          {
            Header: "Flux",
            accessor: "Data.Flux.24hUSD",
            Cell: ({cell: {value}}) => {
              const val = toCurrency(value)
              return('$' + val)
            }
          },
          {
            Header: "Ergo",
            accessor: "Data.Ergo.24hUSD",
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
    <div className="App">
      <Table columns={columns} data={data} />
    </div>
  );
}

export default App;