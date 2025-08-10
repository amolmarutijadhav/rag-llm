# Performance Benchmarks

This directory contains performance benchmarking scripts for the Enhanced Chat Completion Service.

## Scripts

### `performance_benchmark.py`
Comprehensive performance benchmarking script that measures:
- Response times across different conversation lengths
- API call counts (embedding, vector search, LLM)
- Parallel vs sequential processing performance
- Detailed metrics and analysis

**Usage:**
```bash
cd scripts/benchmarks
python performance_benchmark.py
```

### `performance_comparison.py`
Focused comparison script that compares:
- Single query vs multi-query approaches
- Performance impact of enhanced features
- Cost analysis and optimization recommendations

**Usage:**
```bash
cd scripts/benchmarks
python performance_comparison.py
```

## Prerequisites

1. Activate the virtual environment:
   ```bash
   .venv\Scripts\Activate.ps1
   ```

2. Set Python path (for module imports):
   ```bash
   $env:PYTHONPATH = "."
   ```

3. Have test data loaded in the vector store

**Note**: These scripts work directly with the services and do NOT require the FastAPI server to be running.

## Output

- Console output with detailed performance metrics
- JSON files with raw benchmark data (saved to `../reports/performance/`)
- Performance analysis and recommendations

## Configuration

Both scripts use the configuration from `app/core/enhanced_chat_config.py`:
- `enable_parallel_processing`: Enable/disable parallel processing
- `max_concurrent_queries`: Maximum concurrent API calls
- `max_processing_time_ms`: Timeout for processing

## Notes

- Scripts make real API calls to OpenAI and Qdrant
- Results may vary based on network conditions and API response times
- Consider running multiple times for more accurate averages
- Monitor API usage and costs when running benchmarks
