/**
 * Refactored DataTable component with improved code quality.
 * 
 * This component demonstrates:
 * - Proper TypeScript interfaces
 * - Separated concerns and smaller functions
 * - Better error handling and accessibility
 * - Optimized performance with proper memoization
 */

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import axios, { CancelTokenSource } from 'axios';
import {
  TableColumn,
  SortConfiguration,
  SortDirection,
  User,
  APIResponse,
  PaginatedResponse,
  LoadingState,
  ErrorState
} from '../types';
import { ArrayUtils, APIUtils, StringUtils } from '../utils';

interface DataTableProps<T = any> {
  endpoint: string;
  columns: TableColumn<T>[];
  onRowClick?: (row: T) => void;
  onSelectionChange?: (selectedRows: T[]) => void;
  refreshInterval?: number;
  pageSize?: number;
  searchable?: boolean;
  sortable?: boolean;
  selectable?: boolean;
  className?: string;
  emptyMessage?: string;
  loadingComponent?: React.ComponentType;
  errorComponent?: React.ComponentType<{ error: string; onRetry: () => void }>;
}

interface TableState<T> {
  data: T[];
  loading: LoadingState;
  error: ErrorState;
  searchTerm: string;
  sortConfig: SortConfiguration | null;
  selectedRows: Set<number>;
  currentPage: number;
  totalCount: number;
}

// Custom hooks for data fetching
const useDataFetching = <T,>(endpoint: string, refreshInterval?: number) => {
  const [state, setState] = useState<TableState<T>>({
    data: [],
    loading: { isLoading: true },
    error: { hasError: false },
    searchTerm: '',
    sortConfig: null,
    selectedRows: new Set(),
    currentPage: 1,
    totalCount: 0
  });

  const cancelTokenRef = useRef<CancelTokenSource | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchData = useCallback(async (params: {
    search?: string;
    sort?: SortConfiguration;
    page?: number;
    pageSize?: number;
  } = {}) => {
    try {
      setState(prev => ({ ...prev, loading: { isLoading: true } }));

      // Cancel previous request
      if (cancelTokenRef.current) {
        cancelTokenRef.current.cancel('New request initiated');
      }

      // Create new cancel token
      cancelTokenRef.current = axios.CancelToken.source();

      // Build query parameters
      const queryParams = APIUtils.buildQueryString({
        search: params.search || '',
        sortBy: params.sort?.column || '',
        sortDirection: params.sort?.direction || '',
        page: params.page || 1,
        pageSize: params.pageSize || 20
      });

      const url = `${endpoint}${queryParams ? `?${queryParams}` : ''}`;

      const response = await axios.get<APIResponse<PaginatedResponse<T>>>(url, {
        cancelToken: cancelTokenRef.current.token,
        timeout: 10000
      });

      if (APIUtils.isSuccessResponse(response.data)) {
        const { items, totalCount } = response.data.data!;
        setState(prev => ({
          ...prev,
          data: items,
          totalCount,
          loading: { isLoading: false },
          error: { hasError: false }
        }));
      } else {
        throw new Error(APIUtils.getErrorMessage(response.data));
      }
    } catch (error: any) {
      if (axios.isCancel(error)) {
        return; // Request was cancelled, don't update state
      }

      const errorMessage = error.response?.data?.message || error.message || 'Failed to load data';
      setState(prev => ({
        ...prev,
        loading: { isLoading: false },
        error: { hasError: true, error: errorMessage }
      }));
    }
  }, [endpoint]);

  const retryFetch = useCallback(() => {
    fetchData({
      search: state.searchTerm,
      sort: state.sortConfig || undefined,
      page: state.currentPage
    });
  }, [fetchData, state.searchTerm, state.sortConfig, state.currentPage]);

  // Setup polling
  useEffect(() => {
    fetchData();

    if (refreshInterval && refreshInterval > 0) {
      intervalRef.current = setInterval(() => {
        fetchData({
          search: state.searchTerm,
          sort: state.sortConfig || undefined,
          page: state.currentPage
        });
      }, refreshInterval);
    }

    return () => {
      if (cancelTokenRef.current) {
        cancelTokenRef.current.cancel('Component unmounted');
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [endpoint, refreshInterval]);

  return {
    ...state,
    setState,
    fetchData,
    retryFetch
  };
};

// Sorting logic
const useSorting = <T,>(
  data: T[],
  onSortChange?: (sortConfig: SortConfiguration) => void
) => {
  const [sortConfig, setSortConfig] = useState<SortConfiguration | null>(null);

  const handleSort = useCallback((column: string) => {
    const newSortConfig: SortConfiguration = {
      column,
      direction: sortConfig?.column === column && sortConfig.direction === SortDirection.ASC
        ? SortDirection.DESC
        : SortDirection.ASC
    };

    setSortConfig(newSortConfig);
    onSortChange?.(newSortConfig);
  }, [sortConfig, onSortChange]);

  const sortedData = useMemo(() => {
    if (!sortConfig) return data;

    return ArrayUtils.sortBy(
      data,
      [(item: T) => (item as any)[sortConfig.column]],
      [sortConfig.direction]
    );
  }, [data, sortConfig]);

  return {
    sortConfig,
    sortedData,
    handleSort
  };
};

// Search functionality
const useSearch = <T,>(
  data: T[],
  columns: TableColumn<T>[],
  onSearchChange?: (searchTerm: string) => void
) => {
  const [searchTerm, setSearchTerm] = useState('');

  const debouncedSearch = useMemo(
    () => APIUtils.debounce((term: string) => {
      onSearchChange?.(term);
    }, 300),
    [onSearchChange]
  );

  const handleSearchChange = useCallback((term: string) => {
    setSearchTerm(term);
    debouncedSearch(term);
  }, [debouncedSearch]);

  const filteredData = useMemo(() => {
    if (!searchTerm.trim()) return data;

    const lowerSearchTerm = searchTerm.toLowerCase();
    return data.filter(row => {
      return columns.some(column => {
        const value = (row as any)[column.key];
        if (value == null) return false;
        return String(value).toLowerCase().includes(lowerSearchTerm);
      });
    });
  }, [data, searchTerm, columns]);

  return {
    searchTerm,
    filteredData,
    handleSearchChange
  };
};

// Row selection logic
const useRowSelection = <T extends { id: number },>(
  data: T[],
  onSelectionChange?: (selectedRows: T[]) => void
) => {
  const [selectedRowIds, setSelectedRowIds] = useState<Set<number>>(new Set());

  const handleRowSelect = useCallback((rowId: number) => {
    setSelectedRowIds(prev => {
      const newSelection = new Set(prev);
      if (newSelection.has(rowId)) {
        newSelection.delete(rowId);
      } else {
        newSelection.add(rowId);
      }
      return newSelection;
    });
  }, []);

  const handleSelectAll = useCallback(() => {
    const allIds = data.map(row => row.id);
    const allSelected = allIds.every(id => selectedRowIds.has(id));
    
    if (allSelected) {
      setSelectedRowIds(new Set());
    } else {
      setSelectedRowIds(new Set(allIds));
    }
  }, [data, selectedRowIds]);

  const selectedRows = useMemo(() => {
    return data.filter(row => selectedRowIds.has(row.id));
  }, [data, selectedRowIds]);

  useEffect(() => {
    onSelectionChange?.(selectedRows);
  }, [selectedRows, onSelectionChange]);

  return {
    selectedRowIds,
    selectedRows,
    handleRowSelect,
    handleSelectAll
  };
};

// Cell rendering utilities
const CellRenderer = {
  renderText: (value: any): string => {
    if (value == null) return '';
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    if (typeof value === 'number') return value.toLocaleString();
    return StringUtils.truncate(String(value), 100);
  },

  renderSafeHtml: (value: string): React.ReactNode => {
    // Always escape HTML to prevent XSS
    return StringUtils.stripHtml(value);
  },

  renderWithCustomRenderer: <T,>(
    value: any,
    row: T,
    renderer?: (value: any, row: T) => React.ReactNode
  ): React.ReactNode => {
    if (renderer) {
      try {
        return renderer(value, row);
      } catch (error) {
        console.error('Cell renderer error:', error);
        return 'Error';
      }
    }
    return CellRenderer.renderText(value);
  }
};

// Main component
const RefactoredDataTable = <T extends { id: number },>({
  endpoint,
  columns,
  onRowClick,
  onSelectionChange,
  refreshInterval = 0,
  pageSize = 20,
  searchable = true,
  sortable = true,
  selectable = false,
  className = '',
  emptyMessage = 'No data available',
  loadingComponent: LoadingComponent,
  errorComponent: ErrorComponent
}: DataTableProps<T>): React.ReactElement => {
  const {
    data,
    loading,
    error,
    fetchData,
    retryFetch
  } = useDataFetching<T>(endpoint, refreshInterval);

  const { searchTerm, filteredData, handleSearchChange } = useSearch(
    data,
    columns,
    (term) => fetchData({ search: term })
  );

  const { sortConfig, sortedData, handleSort } = useSorting(
    filteredData,
    (config) => fetchData({ sort: config })
  );

  const {
    selectedRowIds,
    selectedRows,
    handleRowSelect,
    handleSelectAll
  } = useRowSelection(sortedData, onSelectionChange);

  const handleRowClick = useCallback((row: T) => {
    onRowClick?.(row);
  }, [onRowClick]);

  const handleKeyDown = useCallback((event: React.KeyboardEvent, action: () => void) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      action();
    }
  }, []);

  // Render loading state
  if (loading.isLoading && data.length === 0) {
    return LoadingComponent ? (
      <LoadingComponent />
    ) : (
      <div className="data-table-loading" role="status" aria-live="polite">
        <div className="loading-spinner" />
        <span>Loading data...</span>
      </div>
    );
  }

  // Render error state
  if (error.hasError) {
    return ErrorComponent ? (
      <ErrorComponent error={String(error.error)} onRetry={retryFetch} />
    ) : (
      <div className="data-table-error" role="alert">
        <h3>Error Loading Data</h3>
        <p>{String(error.error)}</p>
        <button onClick={retryFetch} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className={`refactored-data-table ${className}`}>
      {/* Search input */}
      {searchable && (
        <div className="table-controls">
          <div className="search-container">
            <label htmlFor="table-search" className="sr-only">
              Search table data
            </label>
            <input
              id="table-search"
              type="search"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="search-input"
              aria-label="Search table data"
              autoComplete="off"
            />
          </div>
        </div>
      )}

      {/* Selection summary */}
      {selectable && selectedRows.length > 0 && (
        <div className="selection-summary" role="status" aria-live="polite">
          {selectedRows.length} item{selectedRows.length !== 1 ? 's' : ''} selected
        </div>
      )}

      {/* Data table */}
      <div className="table-container" role="region" aria-label="Data table">
        <table className="data-table" role="table">
          <thead>
            <tr role="row">
              {selectable && (
                <th role="columnheader">
                  <input
                    type="checkbox"
                    checked={data.length > 0 && data.every(row => selectedRowIds.has(row.id))}
                    onChange={handleSelectAll}
                    aria-label="Select all rows"
                  />
                </th>
              )}
              {columns.map((column) => (
                <th
                  key={String(column.key)}
                  role="columnheader"
                  style={{ width: column.width, textAlign: column.align }}
                  aria-sort={
                    sortConfig?.column === column.key
                      ? sortConfig.direction === SortDirection.ASC
                        ? 'ascending'
                        : 'descending'
                      : 'none'
                  }
                >
                  {sortable && column.sortable !== false ? (
                    <button
                      className="column-header-button"
                      onClick={() => handleSort(String(column.key))}
                      onKeyDown={(e) => handleKeyDown(e, () => handleSort(String(column.key)))}
                      aria-label={`Sort by ${column.label}`}
                    >
                      {column.headerRender ? column.headerRender() : column.label}
                      {sortConfig?.column === column.key && (
                        <span className="sort-indicator" aria-hidden="true">
                          {sortConfig.direction === SortDirection.ASC ? ' ↑' : ' ↓'}
                        </span>
                      )}
                    </button>
                  ) : (
                    <span>{column.headerRender ? column.headerRender() : column.label}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length + (selectable ? 1 : 0)} className="empty-message">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              sortedData.map((row, index) => (
                <tr
                  key={row.id}
                  role="row"
                  className={selectedRowIds.has(row.id) ? 'selected' : ''}
                  onClick={() => handleRowClick(row)}
                  onKeyDown={(e) => handleKeyDown(e, () => handleRowClick(row))}
                  tabIndex={onRowClick ? 0 : -1}
                  style={{ cursor: onRowClick ? 'pointer' : 'default' }}
                  aria-selected={selectedRowIds.has(row.id)}
                >
                  {selectable && (
                    <td role="gridcell">
                      <input
                        type="checkbox"
                        checked={selectedRowIds.has(row.id)}
                        onChange={() => handleRowSelect(row.id)}
                        aria-label={`Select row ${index + 1}`}
                        onClick={(e) => e.stopPropagation()}
                      />
                    </td>
                  )}
                  {columns.map((column) => (
                    <td
                      key={String(column.key)}
                      role="gridcell"
                      style={{ textAlign: column.align }}
                    >
                      {CellRenderer.renderWithCustomRenderer(
                        (row as any)[column.key],
                        row,
                        column.render
                      )}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Loading overlay for subsequent loads */}
      {loading.isLoading && data.length > 0 && (
        <div className="loading-overlay" aria-live="polite">
          Updating...
        </div>
      )}

      {/* Debug info (development only) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="debug-info">
          <details>
            <summary>Debug Information</summary>
            <pre>
              {JSON.stringify({
                totalRows: data.length,
                filteredRows: filteredData.length,
                sortedRows: sortedData.length,
                selectedRows: selectedRows.length,
                searchTerm,
                sortConfig
              }, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
};

export default React.memo(RefactoredDataTable) as typeof RefactoredDataTable;