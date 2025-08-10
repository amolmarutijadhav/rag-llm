# Performance Reports

This directory contains generated performance reports and analysis data from benchmarking runs.

## Report Files

### `performance_benchmark_YYYYMMDD_HHMMSS.json`
Comprehensive benchmark results including:
- Response times for different conversation lengths
- API call metrics (embedding, vector search, LLM)
- Parallel vs sequential processing comparison
- Detailed run-by-run data

### `performance_comparison_YYYYMMDD_HHMMSS.json`
Comparison analysis between:
- Single query vs multi-query approaches
- Performance impact analysis
- Cost implications
- Optimization recommendations

## Report Structure

### Benchmark Reports
```json
{
  "1_turns": {
    "summary": {
      "total_runs": 3,
      "avg_total_time": 5.658,
      "avg_embedding_calls": 8.0,
      "avg_vector_search_calls": 8.0,
      "parallel_processing_used": false
    },
    "detailed_metrics": [...]
  },
  "3_turns": {...},
  "5_turns": {...}
}
```

### Comparison Reports
```json
{
  "single_query": [...],
  "multi_query": [...],
  "analysis": {
    "single_query": {...},
    "multi_query": {...},
    "comparison": {
      "time_increase": 180.4,
      "embedding_calls_increase": 14.3,
      "vector_calls_increase": 14.3
    }
  }
}
```

## Key Metrics

- **Response Time**: Total processing time in seconds
- **API Calls**: Number of embedding, vector search, and LLM calls
- **Queries Generated**: Number of enhanced queries created
- **Parallel Processing**: Whether parallel processing was enabled
- **Cost Impact**: Estimated cost increase vs single query

## Usage

These reports are automatically generated when running:
- `scripts/benchmarks/performance_benchmark.py`
- `scripts/benchmarks/performance_comparison.py`

Reports can be used for:
- Performance trend analysis
- Optimization planning
- Cost analysis
- Production deployment decisions

## Analysis

See `doc/performance/PERFORMANCE_ANALYSIS.md` for detailed analysis and recommendations based on these reports.
