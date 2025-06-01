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

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import axios, { CancelTokenSource } from 'axios';
import ErrorBoundary from './ErrorBoundary';

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
  
  const cancelTokenRef = useRef<CancelTokenSource | null>(null);
  
  useEffect(() => {
    const interval = setInterval(() => {
      fetchData();
    }, 5000);
    
    fetchData();
    
    // Cleanup function
    return () => {
      clearInterval(interval);
      if (cancelTokenRef.current) {
        cancelTokenRef.current.cancel('Component unmounted');
      }
    };
  }, [endpoint]);
  
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Cancel previous request if still pending
      if (cancelTokenRef.current) {
        cancelTokenRef.current.cancel('New request initiated');
      }
      
      // Create new cancel token
      cancelTokenRef.current = axios.CancelToken.source();
      
      const response = await axios.get(endpoint, {
        cancelToken: cancelTokenRef.current.token,
        timeout: 10000 // 10 second timeout
      });
      
      // Validate response data
      if (!Array.isArray(response.data)) {
        throw new Error('Invalid data format received from server');
      }
      
      setApiResponseCache(prev => ({
        ...prev,
        [endpoint]: response.data
      }));
      
      setData(response.data);
    } catch (err: any) {
      if (axios.isCancel(err)) {
        console.log('Request cancelled:', err.message);
        return;
      }
      
      // Log error for debugging (don't expose to user)
      console.error('Data fetch error:', err);
      
      // Set user-friendly error message
      if (err.code === 'ECONNABORTED') {
        setError('Request timed out. Please try again.');
      } else if (err.response?.status === 404) {
        setError('Data not found.');
      } else if (err.response?.status >= 500) {
        setError('Server error. Please try again later.');
      } else {
        setError('Failed to load data. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [endpoint]);
  
  // Memoized filtering with proper error handling
  const filteredData = useMemo(() => {
    if (!searchTerm.trim()) return data;
    
    return data.filter(row => {
      try {
        return columns.some(column => {
          const cellValue = row[column];
          if (cellValue == null) return false;
          return cellValue.toString().toLowerCase().includes(searchTerm.toLowerCase());
        });
      } catch (error) {
        console.error('Error filtering row:', error, row);
        return false;
      }
    });
  }, [data, searchTerm, columns]);
  
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
  
  // Safe cell rendering without XSS vulnerabilities
  const renderCell = useCallback((value: any) => {
    try {
      if (value == null) return '';
      
      // Always escape HTML content to prevent XSS
      const stringValue = String(value);
      
      // Handle different data types safely
      if (typeof value === 'boolean') {
        return value ? 'Yes' : 'No';
      }
      
      if (typeof value === 'number') {
        return value.toLocaleString();
      }
      
      // Truncate very long strings
      if (stringValue.length > 100) {
        return stringValue.substring(0, 100) + '...';
      }
      
      return stringValue;
    } catch (error) {
      console.error('Error rendering cell:', error, value);
      return 'Error';
    }
  }, []);
  
  // INTENTIONAL ISSUE: No loading state for sorting/filtering
  if (loading && data.length === 0) {
    return <div>Loading...</div>;
  }
  
  if (error) {
    // INTENTIONAL ISSUE: Exposing error details to user
    return <div style={{ color: 'red' }}>Error: {error}</div>;
  }
  
  return (
    <ErrorBoundary>
      <div className="data-table">
        <label htmlFor="search-input" className="sr-only">Search table data</label>
        <input
          id="search-input"
          type="text"
          placeholder="Search..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          aria-label="Search table data"
        />
        
        <table role="table" aria-label="Data table">
          <thead>
            <tr>
              {columns.map(column => (
                <th 
                  key={column}
                  onClick={() => handleSort(column)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handleSort(column);
                    }
                  }}
                  tabIndex={0}
                  role="columnheader"
                  aria-sort={
                    sortColumn === column 
                      ? sortDirection === 'asc' ? 'ascending' : 'descending'
                      : 'none'
                  }
                  style={{ cursor: 'pointer' }}
                >
                  {column}
                  {sortColumn === column && (
                    <span aria-hidden="true">{sortDirection === 'asc' ? ' ↑' : ' ↓'}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {memoizedData.map((row, index) => {
              // Use row ID if available, fallback to index
              const key = row.id || `row-${index}`;
              return (
                <tr 
                  key={key}
                  onClick={() => onRowClick && onRowClick(row)}
                  onKeyDown={(e) => {
                    if ((e.key === 'Enter' || e.key === ' ') && onRowClick) {
                      e.preventDefault();
                      onRowClick(row);
                    }
                  }}
                  tabIndex={onRowClick ? 0 : -1}
                  role={onRowClick ? 'button' : undefined}
                  style={{ cursor: onRowClick ? 'pointer' : 'default' }}
                >
                  {columns.map(column => (
                    <td key={column}>
                      {renderCell(row[column])}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
        
        {/* Only show debug info in development */}
        {process.env.NODE_ENV === 'development' && (
          <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '10px' }}>
            <h4>Debug Info:</h4>
            <p>Total rows: {data.length}</p>
            <p>Filtered rows: {filteredData.length}</p>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
};

// Add prop validation with default values
DataTable.defaultProps = {
  onRowClick: undefined
};

export default React.memo(DataTable);