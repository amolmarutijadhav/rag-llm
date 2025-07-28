import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.domain.services.conversation_aware_rag_service import ConversationAwareRAGService
from app.domain.services.rag_service import RAGService
from app.domain.services.conversation.analyzer import ConversationAnalyzer
from app.domain.models.conversation import ConversationContext, ConversationAnalysisResult, EnhancedQuery
from app.domain.models.requests import ChatMessage
from app.domain.interfaces.providers import EmbeddingProvider, LLMProvider, VectorStoreProvider


@pytest.mark.unit
class TestConversationAwareRAGService:
    """Test suite for Conversation-Aware RAG service."""

    @pytest.fixture
    def mock_rag_service(self):
        """Mock RAG service."""
        mock = Mock(spec=RAGService)
        mock.ask_question = AsyncMock(return_value={
            "success": True,
            "answer": "Test answer",
            "sources": [{"content": "test", "source": "test.txt", "score": 0.9}],
            "question": "test question"
        })
        mock.add_document = AsyncMock(return_value={"success": True, "message": "Document added"})
        mock.add_text = AsyncMock(return_value={"success": True, "message": "Text added"})
        mock.get_stats = Mock(return_value={"success": True, "total_documents": 10})
        mock.clear_knowledge_base = Mock(return_value={"success": True, "message": "Cleared"})
        return mock

    @pytest.fixture
    def mock_conversation_analyzer(self):
        """Mock conversation analyzer."""
        mock = Mock(spec=ConversationAnalyzer)
        mock.analyze_conversation = AsyncMock(return_value=ConversationAnalysisResult(
            context=ConversationContext(
                topics=["technology", "programming"],
                entities=["Python", "API"],
                context_clues=["important", "critical"]
            ),
            confidence_score=0.8,
            analysis_method="hybrid",
            processing_time_ms=150.0
        ))
        mock.generate_enhanced_queries = AsyncMock(return_value=EnhancedQuery(
            original_query="What is Python?",
            enhanced_queries=["What is Python?", "What is Python? technology programming", "What is Python? Python API"],
            context_used=ConversationContext(),
            query_generation_method="conversation_context_enhancement"
        ))
        return mock

    @pytest.fixture
    def mock_embedding_provider(self):
        """Mock embedding provider."""
        mock = Mock(spec=EmbeddingProvider)
        mock.get_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
        return mock

    @pytest.fixture
    def mock_llm_provider(self):
        """Mock LLM provider."""
        mock = Mock(spec=LLMProvider)
        mock.call_llm = AsyncMock(return_value="Test answer")
        return mock

    @pytest.fixture
    def mock_vector_store_provider(self):
        """Mock vector store provider."""
        mock = Mock(spec=VectorStoreProvider)
        mock.search_vectors = AsyncMock(return_value=[
            {
                "payload": {
                    "content": "Python is a programming language",
                    "metadata": {"source": "test.txt"}
                },
                "score": 0.95
            }
        ])
        return mock

    @pytest.fixture
    def conversation_aware_rag_service(self, mock_rag_service, mock_conversation_analyzer):
        """Conversation-aware RAG service with mocked dependencies."""
        return ConversationAwareRAGService(
            rag_service=mock_rag_service,
            conversation_analyzer=mock_conversation_analyzer
        )

    @pytest.fixture
    def sample_messages(self):
        """Sample chat messages for testing."""
        return [
            ChatMessage(role="user", content="What is Python?"),
            ChatMessage(role="assistant", content="Python is a programming language."),
            ChatMessage(role="user", content="How does it compare to Java?"),
            ChatMessage(role="assistant", content="Python and Java are both programming languages but have different characteristics."),
            ChatMessage(role="user", content="Tell me more about Python's features.")
        ]

    @pytest.mark.asyncio
    async def test_ask_question_with_conversation_success(self, conversation_aware_rag_service, 
                                                        mock_conversation_analyzer, sample_messages):
        """Test successful conversation-aware question asking."""
        # Mock the internal methods
        with patch.object(conversation_aware_rag_service, '_perform_multi_query_retrieval') as mock_retrieval, \
             patch.object(conversation_aware_rag_service, '_generate_answer_with_context') as mock_answer:
            
            mock_retrieval.return_value = [[
                {
                    "payload": {
                        "content": "Python is a programming language",
                        "metadata": {"source": "test.txt"}
                    },
                    "score": 0.95
                }
            ]]
            
            mock_answer.return_value = {
                "success": True,
                "answer": "Python is a programming language.",
                "sources": [{"content": "test", "source": "test.txt", "score": 0.95}],
                "question": "Tell me more about Python's features."
            }
            
            result = await conversation_aware_rag_service.ask_question_with_conversation(
                messages=sample_messages,
                current_question="Tell me more about Python's features.",
                top_k=3
            )
            
            assert result["success"] == True
            assert "Python" in result["answer"]
            assert result["conversation_context_used"] == True
            assert "conversation_analysis" in result
            assert "enhanced_queries" in result
            assert "conversation_context" in result

    @pytest.mark.asyncio
    async def test_ask_question_with_conversation_fallback(self, conversation_aware_rag_service, 
                                                         mock_conversation_analyzer, sample_messages):
        """Test conversation-aware question with fallback to original RAG service."""
        # Mock conversation analyzer to raise exception
        mock_conversation_analyzer.analyze_conversation.side_effect = Exception("Analysis failed")
        
        result = await conversation_aware_rag_service.ask_question_with_conversation(
            messages=sample_messages,
            current_question="Tell me more about Python's features.",
            top_k=3
        )
        
        assert result["conversation_context_used"] == False
        assert "fallback_reason" in result
        assert "Analysis failed" in result["fallback_reason"]

    @pytest.mark.asyncio
    async def test_perform_multi_query_retrieval(self, conversation_aware_rag_service, 
                                               mock_embedding_provider, mock_vector_store_provider):
        """Test multi-query retrieval functionality."""
        # Set up the service with mocked providers
        conversation_aware_rag_service.rag_service.embedding_provider = mock_embedding_provider
        conversation_aware_rag_service.rag_service.vector_store_provider = mock_vector_store_provider
        
        queries = ["What is Python?", "Python programming language", "Python features"]
        
        results = await conversation_aware_rag_service._perform_multi_query_retrieval(queries, 3)
        
        assert len(results) == 3
        assert all(isinstance(result, list) for result in results)
        assert mock_embedding_provider.get_embeddings.call_count == 3
        assert mock_vector_store_provider.search_vectors.call_count == 3

    def test_merge_and_deduplicate_results(self, conversation_aware_rag_service):
        """Test merging and deduplicating results."""
        all_results = [
            [
                {
                    "payload": {"content": "Python is a programming language", "metadata": {"source": "test1.txt"}},
                    "score": 0.95
                },
                {
                    "payload": {"content": "Java is another language", "metadata": {"source": "test2.txt"}},
                    "score": 0.85
                }
            ],
            [
                {
                    "payload": {"content": "Python is a programming language", "metadata": {"source": "test1.txt"}},
                    "score": 0.90
                },
                {
                    "payload": {"content": "JavaScript is a scripting language", "metadata": {"source": "test3.txt"}},
                    "score": 0.80
                }
            ]
        ]
        
        merged_results = conversation_aware_rag_service._merge_and_deduplicate_results(all_results)
        
        # Should have 3 unique results (Python, Java, JavaScript)
        assert len(merged_results) == 3
        # Should be sorted by score (highest first)
        assert merged_results[0]["score"] >= merged_results[1]["score"]
        assert merged_results[1]["score"] >= merged_results[2]["score"]

    @pytest.mark.asyncio
    async def test_generate_answer_with_context(self, conversation_aware_rag_service, 
                                              mock_llm_provider):
        """Test answer generation with context."""
        conversation_aware_rag_service.rag_service.llm_provider = mock_llm_provider
        
        results = [
            {
                "payload": {
                    "content": "Python is a programming language created by Guido van Rossum",
                    "metadata": {"source": "test.txt"}
                },
                "score": 0.95
            }
        ]
        
        context = ConversationContext(topics=["programming"], entities=["Python"])
        
        result = await conversation_aware_rag_service._generate_answer_with_context(
            "What is Python?", results, context
        )
        
        assert result["success"] == True
        assert "Python" in result["answer"]
        assert len(result["sources"]) == 1
        assert mock_llm_provider.call_llm.called

    @pytest.mark.asyncio
    async def test_generate_answer_with_context_no_results(self, conversation_aware_rag_service):
        """Test answer generation with no results."""
        result = await conversation_aware_rag_service._generate_answer_with_context(
            "What is Python?", [], ConversationContext()
        )
        
        assert result["success"] == False
        assert "couldn't find" in result["answer"].lower()

    def test_enhance_response_with_context(self, conversation_aware_rag_service):
        """Test response enhancement with conversation context."""
        base_response = {
            "success": True,
            "answer": "Python is a programming language.",
            "sources": [{"content": "test", "source": "test.txt", "score": 0.9}],
            "question": "What is Python?"
        }
        
        analysis_result = ConversationAnalysisResult(
            context=ConversationContext(
                topics=["programming"],
                entities=["Python"],
                context_clues=["important"]
            ),
            confidence_score=0.8,
            analysis_method="hybrid",
            processing_time_ms=150.0
        )
        
        enhanced_query = EnhancedQuery(
            original_query="What is Python?",
            enhanced_queries=["What is Python?", "What is Python? programming"],
            context_used=ConversationContext(),
            query_generation_method="conversation_context_enhancement"
        )
        
        enhanced_response = conversation_aware_rag_service._enhance_response_with_context(
            base_response, analysis_result, enhanced_query
        )
        
        assert enhanced_response["conversation_context_used"] == True
        assert "conversation_analysis" in enhanced_response
        assert "enhanced_queries" in enhanced_response
        assert "conversation_context" in enhanced_response
        assert enhanced_response["conversation_analysis"]["strategy_used"] == "hybrid"
        assert enhanced_response["conversation_analysis"]["confidence_score"] == 0.8

    @pytest.mark.asyncio
    async def test_delegate_methods_to_rag_service(self, conversation_aware_rag_service, mock_rag_service):
        """Test that delegated methods work correctly."""
        # Test add_document
        result = await conversation_aware_rag_service.add_document("test.txt")
        assert result["success"] == True
        mock_rag_service.add_document.assert_called_once_with("test.txt")
        
        # Test add_text
        result = await conversation_aware_rag_service.add_text("test content", "test_source")
        assert result["success"] == True
        mock_rag_service.add_text.assert_called_once_with("test content", "test_source")
        
        # Test get_stats
        result = conversation_aware_rag_service.get_stats()
        assert result["success"] == True
        assert result["conversation_aware"] == True
        assert "available_analysis_strategies" in result
        mock_rag_service.get_stats.assert_called_once()
        
        # Test clear_knowledge_base
        result = conversation_aware_rag_service.clear_knowledge_base()
        assert result["success"] == True
        mock_rag_service.clear_knowledge_base.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_for_single_query(self, conversation_aware_rag_service, 
                                           mock_embedding_provider, mock_vector_store_provider):
        """Test single query retrieval."""
        conversation_aware_rag_service.rag_service.embedding_provider = mock_embedding_provider
        conversation_aware_rag_service.rag_service.vector_store_provider = mock_vector_store_provider
        
        results = await conversation_aware_rag_service._retrieve_for_single_query("What is Python?", 3)
        
        assert len(results) == 1
        assert results[0]["payload"]["content"] == "Python is a programming language"
        assert mock_embedding_provider.get_embeddings.called
        assert mock_vector_store_provider.search_vectors.called

    @pytest.mark.asyncio
    async def test_retrieve_for_single_query_error(self, conversation_aware_rag_service):
        """Test single query retrieval with error."""
        # Mock embedding provider to raise exception
        conversation_aware_rag_service.rag_service.embedding_provider = Mock()
        conversation_aware_rag_service.rag_service.embedding_provider.get_embeddings = AsyncMock(
            side_effect=Exception("Embedding error")
        )
        
        results = await conversation_aware_rag_service._retrieve_for_single_query("What is Python?", 3)
        
        assert results == [] 