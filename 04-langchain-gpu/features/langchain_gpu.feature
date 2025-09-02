Feature: LangChain GPU-Accelerated AI API
  As an AI engineer
  I want to deploy a GPU-accelerated LangChain application
  So that I can perform efficient AI inference and document processing

  Background:
    Given the LangChain GPU application is containerized
    And the required AI models are available
    And GPU drivers are properly installed (if available)

  Scenario: GPU detection and configuration
    Given the container is running
    When I send a GET request to "/"
    Then the response status should be 200
    And the response should contain "device" field
    And the response should contain "cuda_available" field
    And the response should contain "gpu_count" field
    And the device should be either "cpu" or "cuda"

  Scenario: Health check includes GPU information
    Given the container is running
    When I send a GET request to "/health"
    Then the response status should be 200
    And the response should contain "status" field with value "healthy"
    And the response should contain "service" field with value "langchain-gpu-api"
    And the response should contain "device" field
    And if CUDA is available, GPU information should be included

  Scenario: Chat functionality works
    Given the container is running
    And the language model is loaded
    When I send a POST request to "/chat" with message "Hello, how are you?"
    Then the response status should be 200
    And the response should contain "response" field
    And the response should contain "input_length" field
    And the response should contain "output_length" field
    And the response should contain "device_used" field
    And the response text should be non-empty

  Scenario: Chat with different parameters
    Given the container is running
    When I send a POST request to "/chat" with different temperature values
    Then all requests should return status 200
    And responses should vary based on temperature settings
    And higher temperature should produce more creative responses

  Scenario: Document embedding functionality
    Given the container is running
    When I send a POST request to "/embed-documents" with text content
    Then the response status should be 200
    And the response should contain "status" field with value "success"
    And the response should contain "chunks_created" field
    And the response should contain "embedding_model" field
    And the response should contain "device_used" field
    And the chunks_created should be greater than 0

  Scenario: Document querying after embedding
    Given the container is running
    And documents have been embedded successfully
    When I send a POST request to "/query-documents" with a query
    Then the response status should be 200
    And the response should contain "query" field
    And the response should contain "results" field
    And the response should contain "device_used" field
    And the results should be relevant to the query

  Scenario: Query without embedding fails gracefully
    Given the container is running
    And no documents have been embedded
    When I send a POST request to "/query-documents" with a query
    Then the response status should be 400
    And the response should contain an error message about no embedded documents

  Scenario: GPU statistics are available
    Given the container is running
    When I send a GET request to "/gpu-stats"
    Then the response status should be 200
    And if CUDA is available, GPU statistics should be returned
    Or if CUDA is not available, an appropriate message should be returned

  Scenario: Large document processing
    Given the container is running
    When I send a POST request to "/embed-documents" with a large text document
    Then the response should handle the large input appropriately
    And the document should be split into appropriate chunks
    And embedding should complete without errors

  Scenario: Concurrent requests handling
    Given the container is running
    When I send multiple concurrent chat requests
    Then all requests should be processed successfully
    And the model should handle concurrent access properly
    And response times should be reasonable

  Scenario: Model loading and memory management
    Given the container is starting
    When the first AI request is made
    Then the model should be loaded lazily
    And memory usage should be monitored
    And if GPU is available, model should be moved to GPU

  Scenario: Different chunk sizes for embedding
    Given the container is running
    When I embed documents with different chunk_size parameters
    Then each request should return appropriate number of chunks
    And smaller chunk sizes should create more chunks
    And larger chunk sizes should create fewer chunks

  Scenario: Error handling for invalid inputs
    Given the container is running
    When I send requests with invalid parameters
    Then the API should return appropriate error codes
    And error messages should be descriptive
    And the service should remain stable

  Scenario: Performance with GPU acceleration
    Given the container is running with GPU support
    When I perform AI inference tasks
    Then GPU utilization should be observed
    And inference should be faster than CPU-only mode
    And memory should be efficiently managed on GPU
