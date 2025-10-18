# tests/conftest.py
import pytest
from selenium import webdriver

@pytest.fixture
def driver():
    """Fixture para crear y destruir la instancia del driver."""
    # --- SETUP ---
    driver = webdriver.Chrome()
    
    yield driver 
    
    # --- TEARDOWN ---
    driver.quit()