
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# --- 1. Mock External Dependencies setup BEFORE importing the app ---
# This is crucial because the app connects to ES and loads models at import time.

# Mock elasticsearch
mock_es_module = MagicMock()
sys.modules['elasticsearch'] = mock_es_module
sys.modules['elasticsearch.helpers'] = MagicMock()

# Configure the mock Elasticsearch client
mock_es_instance = MagicMock()
# This ensures connect2ES passes the ping check
mock_es_instance.ping.return_value = True 
mock_es_module.Elasticsearch.return_value = mock_es_instance

# Mock tensorflow and tensorflow_hub
sys.modules['tensorflow'] = MagicMock()
sys.modules['tensorflow_hub'] = MagicMock()

# Mock logstash
mock_logstash = MagicMock()
sys.modules['logstash'] = mock_logstash

# Configure mock handler with a valid logging level to satisfy logging module checks
import logging
mock_handler = MagicMock()
mock_handler.level = logging.NOTSET  # Allow all messages
mock_logstash.TCPLogstashHandler.return_value = mock_handler

# --- 2. Add Project Root to Path ---
# Assuming this test file is in <ROOT>/tests/ and app is in <ROOT>/SearchEngine_QA/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- 3. Import the Application ---
try:
    from SearchEngine_QA import searchES_FlaskAPI
except ImportError as e:
    pytest.fail(f"Failed to import application: {e}")

# --- 4. Test Fixtures ---

@pytest.fixture
def client():
    """Configures the Flask application for testing."""
    searchES_FlaskAPI.app.config['TESTING'] = True
    
    # Populate the in-memory databases with predictable test data
    searchES_FlaskAPI.questions_db = {
        '1': {'Id': '1', 'Title': 'How to use pytest?', 'Body': 'I need help with pytest.'},
        '2': {'Id': '2', 'Title': 'Elasticsearch basics', 'Body': 'What is an inverse index?'}
    }
    
    searchES_FlaskAPI.answers_db = {
        '1': [{'Id': '101', 'ParentId': '1', 'Body': 'Use fixtures!', 'Score': '5'}]
    }
    
    with searchES_FlaskAPI.app.test_client() as client:
        yield client

# --- 5. Tests ---

def test_home(client):
    """Test the home page route."""
    # Patch render_template to avoid needing the actual 'index.html' file present
    with patch('SearchEngine_QA.searchES_FlaskAPI.render_template') as mock_render:
        mock_render.return_value = "Home Page"
        rv = client.get('/')
        assert rv.status_code == 200
        assert b"Home Page" in rv.data

def test_details_api_success(client):
    """Test retrieving details for an existing question."""
    rv = client.get('/api/details/1')
    assert rv.status_code == 200
    
    json_data = rv.get_json()
    assert json_data['question']['Title'] == 'How to use pytest?'
    assert len(json_data['answers']) == 1
    assert json_data['answers'][0]['Body'] == 'Use fixtures!'

def test_details_api_not_found(client):
    """Test retrieving details for a non-existent question."""
    rv = client.get('/api/details/999')
    assert rv.status_code == 404
    assert b"Question not found" in rv.data

def test_search_api_integration(client):
    """
    Test the search API endpoint.
    Mocks the underlying search functions to return controlled results.
    """
    mock_hits_kw = {
        'hits': {
            'hits': [
                {'_id': '1', '_score': 2.0, '_source': {'title': 'How to use pytest?'}}
            ]
        }
    }
    
    mock_hits_sem = {
        'hits': {
            'hits': [
                {'_id': '2', '_score': 0.9, '_source': {'title': 'Elasticsearch basics'}}
            ]
        }
    }
    
    # Patch the search functions used by the route
    with patch('SearchEngine_QA.searchES_FlaskAPI.keywordSearch') as mock_kw, \
         patch('SearchEngine_QA.searchES_FlaskAPI.sentenceSimilaritybyNN') as mock_sem:
        
        mock_kw.return_value = mock_hits_kw
        mock_sem.return_value = mock_hits_sem
        
        rv = client.get('/api/search/test_query')
        assert rv.status_code == 200
        
        data = rv.get_json()
        assert len(data) == 2
        
        # Verify both results are present and correctly formatted
        ids = [item['id'] for item in data]
        assert '1' in ids
        assert '2' in ids
        
        # Verify the route called the search logic
        mock_kw.assert_called_once()
        mock_sem.assert_called_once()

def test_keyword_search_logic():
    """Test the keywordSearch function calls Elasticsearch correctly."""
    mock_es = MagicMock()
    mock_response = {'hits': {'hits': []}}
    mock_es.search.return_value = mock_response
    
    query = "testing"
    
    # Call the function directly
    result = searchES_FlaskAPI.keywordSearch(mock_es, query)
    
    assert result == mock_response
    mock_es.search.assert_called_once()
    
    # Verify arguments passed to ES
    call_args = mock_es.search.call_args
    assert call_args[1]['index'] == 'questions-index' # kwargs check
    assert call_args[1]['body']['query']['match']['title'] == query
