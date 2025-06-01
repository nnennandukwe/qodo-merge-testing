/**
 * DataTable component with intentional performance and security issues
 * 
 * INTENTIONAL ISSUES:
 * - Performance problems with large datasets
 * - Memory leaks
 * - Insecure data handling
 * - Poor accessibility
 * - Type safety issues
 */

import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';

// INTENTIONAL ISSUE: Loose typing
interface TableData {
  [key: string]: any; // Should be more specific
}

interface DataTableProps {
  endpoint: string;
  columns: string[];
  onRowClick?: (row: any) => void;
}

const DataTable: React.FC<DataTableProps> = ({ endpoint, columns, onRowClick }) => {
  const [data, setData] = useState<TableData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  
  // INTENTIONAL ISSUE: Memory leak - storing all API responses
  const [apiResponseCache, setApiResponseCache] = useState<{[key: string]: any}>({});
  
  // INTENTIONAL ISSUE: No cleanup of intervals/timers
  useEffect(() => {
    // INTENTIONAL ISSUE: Polling without cleanup
    const interval = setInterval(() => {
      fetchData();
    }, 5000);
    
    fetchData();
    
    // INTENTIONAL ISSUE: Missing cleanup function
  }, [endpoint]);
  
  const fetchData = async () => {
    try {
      setLoading(true);
      
      // INTENTIONAL ISSUE: No request cancellation, race conditions possible
      const response = await axios.get(endpoint);
      
      // INTENTIONAL ISSUE: Storing potentially sensitive data
      setApiResponseCache(prev => ({
        ...prev,
        [endpoint]: response.data
      }));
      
      setData(response.data);
      setError(null);
    } catch (err: any) {
      // INTENTIONAL ISSUE: Exposing full error details
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };
  
  // INTENTIONAL ISSUE: Inefficient filtering - O(n) on every render
  const filteredData = data.filter(row => {
    // INTENTIONAL ISSUE: No null/undefined checks
    return columns.some(column => 
      row[column].toString().toLowerCase().includes(searchTerm.toLowerCase())
    );
  });
  
  // INTENTIONAL ISSUE: Inefficient sorting - not memoized properly
  const sortedData = [...filteredData].sort((a, b) => {
    if (!sortColumn) return 0;
    
    // INTENTIONAL ISSUE: No type checking for sort values
    const aVal = a[sortColumn];
    const bVal = b[sortColumn];
    
    if (sortDirection === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });
  
  // INTENTIONAL ISSUE: No proper memoization dependencies
  const memoizedData = useMemo(() => {
    return sortedData;
  }, [data]); // Missing searchTerm, sortColumn, sortDirection
  
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };
  
  // INTENTIONAL ISSUE: Unsafe HTML rendering
  const renderCell = (value: any) => {
    if (typeof value === 'string' && value.includes('<')) {
      // INTENTIONAL ISSUE: XSS vulnerability
      return <span dangerouslySetInnerHTML={{ __html: value }} />;
    }
    return String(value);
  };
  
  // INTENTIONAL ISSUE: No loading state for sorting/filtering
  if (loading && data.length === 0) {
    return <div>Loading...</div>;
  }
  
  if (error) {
    // INTENTIONAL ISSUE: Exposing error details to user
    return <div style={{ color: 'red' }}>Error: {error}</div>;
  }
  
  return (
    <div className="data-table">
      {/* INTENTIONAL ISSUE: No accessible label for search input */}
      <input
        type="text"
        placeholder="Search..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        // INTENTIONAL ISSUE: No debouncing for search
      />
      
      {/* INTENTIONAL ISSUE: Missing table accessibility attributes */}
      <table>
        <thead>
          <tr>
            {columns.map(column => (
              <th 
                key={column}
                onClick={() => handleSort(column)}
                // INTENTIONAL ISSUE: No keyboard accessibility
                style={{ cursor: 'pointer' }}
              >
                {column}
                {sortColumn === column && (
                  <span>{sortDirection === 'asc' ? ' ↑' : ' ↓'}</span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {/* INTENTIONAL ISSUE: No virtualization for large datasets */}
          {memoizedData.map((row, index) => (
            <tr 
              key={index} // INTENTIONAL ISSUE: Using array index as key
              onClick={() => onRowClick && onRowClick(row)}
              style={{ cursor: onRowClick ? 'pointer' : 'default' }}
            >
              {columns.map(column => (
                <td key={column}>
                  {renderCell(row[column])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      
      {/* INTENTIONAL ISSUE: Exposing debug information */}
      {process.env.NODE_ENV === 'development' && (
        <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '10px' }}>
          <h4>Debug Info:</h4>
          <p>Total rows: {data.length}</p>
          <p>Filtered rows: {filteredData.length}</p>
          <p>Cache size: {Object.keys(apiResponseCache).length}</p>
          <pre style={{ fontSize: '12px', overflow: 'auto', maxHeight: '200px' }}>
            {JSON.stringify(apiResponseCache, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

// INTENTIONAL ISSUE: No default props or prop validation
export default DataTable;