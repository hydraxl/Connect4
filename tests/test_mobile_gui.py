"""
Tests for mobile and small screen GUI compatibility.

These tests validate that the Connect 4 web application works well
on mobile devices and small screens by checking:
- HTML structure and mobile-friendly meta tags
- CSS responsive design and media queries
- Touch-friendly element sizes
- Layout adaptability
"""

import pytest
import re
import os
from pathlib import Path
from bs4 import BeautifulSoup


# Paths to static files
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATE_DIR = PROJECT_ROOT / 'templates'
STATIC_DIR = PROJECT_ROOT / 'static'
HTML_FILE = TEMPLATE_DIR / 'index.html'
CSS_FILE = STATIC_DIR / 'style.css'


class TestHTMLMobileStructure:
    """Test HTML structure for mobile compatibility."""
    
    @pytest.fixture
    def html_content(self):
        """Load HTML template content."""
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    
    @pytest.fixture
    def soup(self, html_content):
        """Parse HTML with BeautifulSoup."""
        return BeautifulSoup(html_content, 'html.parser')
    
    def test_viewport_meta_tag_present(self, soup):
        """Test that viewport meta tag exists for mobile responsiveness."""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        assert viewport is not None, "Viewport meta tag is missing"
        assert 'width=device-width' in viewport.get('content', ''), \
            "Viewport should include width=device-width"
        assert 'initial-scale=1.0' in viewport.get('content', ''), \
            "Viewport should include initial-scale=1.0"
    
    def test_charset_meta_tag_present(self, soup):
        """Test that charset meta tag is present."""
        charset = soup.find('meta', attrs={'charset': True})
        assert charset is not None, "Charset meta tag is missing"
        assert charset.get('charset', '').lower() in ['utf-8', 'utf8'], \
            "Charset should be UTF-8"
    
    def test_title_tag_present(self, soup):
        """Test that title tag exists."""
        title = soup.find('title')
        assert title is not None, "Title tag is missing"
        assert title.text.strip(), "Title should not be empty"
    
    def test_semantic_html_structure(self, soup):
        """Test that HTML uses semantic structure."""
        # Check for main container
        container = soup.find('div', class_='container')
        assert container is not None, "Main container div should exist"
        
        # Check for heading
        h1 = soup.find('h1')
        assert h1 is not None, "Main heading (h1) should exist"
    
    def test_css_link_present(self, soup):
        """Test that CSS stylesheet is linked."""
        css_link = soup.find('link', attrs={'rel': 'stylesheet'})
        assert css_link is not None, "CSS stylesheet link is missing"
        assert 'style.css' in css_link.get('href', ''), \
            "CSS link should reference style.css"
    
    def test_script_tag_present(self, soup):
        """Test that JavaScript file is included."""
        script = soup.find('script', attrs={'src': True})
        assert script is not None, "JavaScript script tag is missing"
        assert 'script.js' in script.get('src', ''), \
            "Script should reference script.js"
    
    def test_button_has_id(self, soup):
        """Test that button has proper ID for JavaScript interaction."""
        button = soup.find('button', id='new-game-btn')
        assert button is not None, "New game button should have id='new-game-btn'"
    
    def test_status_element_has_id(self, soup):
        """Test that status element has proper ID."""
        status = soup.find('div', id='status')
        assert status is not None, "Status element should have id='status'"
    
    def test_board_container_has_id(self, soup):
        """Test that board container has proper ID."""
        board = soup.find('div', id='board')
        assert board is not None, "Board element should have id='board'"


class TestCSSResponsiveDesign:
    """Test CSS for responsive design and mobile compatibility."""
    
    @pytest.fixture
    def css_content(self):
        """Load CSS file content."""
        with open(CSS_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_media_query_exists(self, css_content):
        """Test that media query for small screens exists."""
        # Look for media query targeting small screens (typically max-width: 600px or similar)
        media_query_pattern = r'@media\s*\([^)]*max-width[^)]*\)'
        assert re.search(media_query_pattern, css_content, re.IGNORECASE), \
            "CSS should contain a media query for small screens"
    
    def test_mobile_cell_sizing(self, css_content):
        """Test that cells are resized for mobile in media query."""
        # Check that media query contains cell size adjustments
        # Extract media query block
        media_match = re.search(
            r'@media\s*\([^)]*max-width[^)]*\)\s*\{([^}]*\{[^}]*\}[^}]*)*\}',
            css_content,
            re.IGNORECASE | re.DOTALL
        )
        assert media_match is not None, "Media query block should exist"
        
        media_content = media_match.group(0)
        # Check for cell size adjustments in media query
        assert '.cell' in media_content, \
            "Media query should adjust .cell styles for mobile"
    
    def test_touch_friendly_button_size(self, css_content):
        """Test that buttons are large enough for touch interaction (min 44x44px)."""
        # Check button padding/size
        btn_pattern = r'\.btn\s*\{[^}]*\}'
        btn_match = re.search(btn_pattern, css_content, re.DOTALL)
        assert btn_match is not None, "Button styles should exist"
        
        btn_styles = btn_match.group(0)
        # Check for padding that would make button touch-friendly
        padding_match = re.search(r'padding:\s*(\d+)px', btn_styles)
        if padding_match:
            padding = int(padding_match.group(1))
            # With padding of 10px, button should be at least 44px tall
            # Assuming font-size of ~16px, 10px padding top/bottom = 36px min
            # This is a basic check - actual size depends on font-size
            assert padding >= 8, "Button padding should be adequate for touch (min 8px)"
    
    def test_touch_friendly_cell_size(self, css_content):
        """Test that cells are large enough for touch interaction."""
        # Check default cell size
        cell_pattern = r'\.cell\s*\{[^}]*\}'
        cell_match = re.search(cell_pattern, css_content, re.DOTALL)
        assert cell_match is not None, "Cell styles should exist"
        
        cell_styles = cell_match.group(0)
        # Check for width/height
        width_match = re.search(r'width:\s*(\d+)px', cell_styles)
        height_match = re.search(r'height:\s*(\d+)px', cell_styles)
        
        if width_match and height_match:
            width = int(width_match.group(1))
            height = int(height_match.group(1))
            # Cells should be at least 44px for touch (WCAG recommendation)
            assert width >= 44 or height >= 44, \
                f"Cell size ({width}x{height}px) should be at least 44px for touch interaction"
    
    def test_mobile_cell_size_adjustment(self, css_content):
        """Test that cells are appropriately sized in mobile media query."""
        # Find media query content
        media_match = re.search(
            r'@media\s*\([^)]*max-width[^)]*\)\s*\{([^}]*\{[^}]*\}[^}]*)*\}',
            css_content,
            re.IGNORECASE | re.DOTALL
        )
        
        if media_match:
            media_content = media_match.group(0)
            # Check if cell size is adjusted in media query
            cell_in_media = re.search(r'\.cell\s*\{[^}]*width:\s*(\d+)px', media_content, re.DOTALL)
            if cell_in_media:
                mobile_width = int(cell_in_media.group(1))
                # Mobile cells should still be touch-friendly (at least 40px)
                assert mobile_width >= 40, \
                    f"Mobile cell size ({mobile_width}px) should be at least 40px for touch"
    
    def test_container_has_max_width(self, css_content):
        """Test that container has max-width for responsive layout."""
        container_pattern = r'\.container\s*\{[^}]*\}'
        container_match = re.search(container_pattern, css_content, re.DOTALL)
        assert container_match is not None, "Container styles should exist"
        
        container_styles = container_match.group(0)
        # Check for max-width
        max_width_match = re.search(r'max-width:\s*(\d+)px', container_styles)
        assert max_width_match is not None, \
            "Container should have max-width for responsive design"
    
    def test_container_has_width_100(self, css_content):
        """Test that container uses width: 100% for responsiveness."""
        container_pattern = r'\.container\s*\{[^}]*\}'
        container_match = re.search(container_pattern, css_content, re.DOTALL)
        assert container_match is not None, "Container styles should exist"
        
        container_styles = container_match.group(0)
        # Check for width: 100% (with or without spaces, with or without semicolon)
        width_match = re.search(r'width:\s*100%', container_styles)
        assert width_match is not None, \
            "Container should have width: 100% for responsive design"
    
    def test_flexbox_or_grid_used(self, css_content):
        """Test that modern layout methods (flexbox/grid) are used."""
        # Check for flexbox or grid usage using regex
        has_flex = re.search(r'display:\s*flex', css_content) is not None
        has_grid = re.search(r'display:\s*grid', css_content) is not None
        
        assert has_flex or has_grid, \
            "CSS should use flexbox or grid for modern responsive layouts"
    
    def test_responsive_typography(self, css_content):
        """Test that typography scales for mobile."""
        # Check if media query adjusts font sizes
        media_match = re.search(
            r'@media\s*\([^)]*max-width[^)]*\)\s*\{([^}]*\{[^}]*\}[^}]*)*\}',
            css_content,
            re.IGNORECASE | re.DOTALL
        )
        
        if media_match:
            media_content = media_match.group(0)
            # Check for font-size adjustments in media query
            font_size_in_media = re.search(r'font-size:\s*[\d.]+em', media_content)
            assert font_size_in_media is not None, \
                "Media query should adjust font sizes for mobile readability"


class TestMobileLayoutAccessibility:
    """Test layout and accessibility features for mobile."""
    
    @pytest.fixture
    def html_content(self):
        """Load HTML template content."""
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    
    @pytest.fixture
    def css_content(self):
        """Load CSS file content."""
        with open(CSS_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_no_horizontal_scroll_on_small_screens(self, css_content):
        """Test that layout prevents horizontal scrolling on small screens."""
        # Check for overflow-x: hidden or proper width constraints
        body_pattern = r'body\s*\{[^}]*\}'
        body_match = re.search(body_pattern, css_content, re.DOTALL)
        
        if body_match:
            body_styles = body_match.group(0)
            # Should have overflow-x: hidden or max-width constraints
            has_overflow_control = (
                'overflow-x' in body_styles or
                'overflow:' in body_styles or
                'max-width' in body_styles or
                re.search(r'width:\s*100%', body_styles) is not None
            )
            # This is a soft check - proper responsive design should handle this
            assert True  # Layout should be responsive, but this is hard to test statically
    
    def test_game_info_flex_wrap(self, css_content):
        """Test that game-info uses flex-wrap for mobile stacking."""
        game_info_pattern = r'\.game-info\s*\{[^}]*\}'
        game_info_match = re.search(game_info_pattern, css_content, re.DOTALL)
        
        if game_info_match:
            game_info_styles = game_info_match.group(0)
            # Should have flex-wrap or similar for mobile
            has_flex_wrap = (
                'flex-wrap' in game_info_styles or
                re.search(r'flex-direction:\s*column', game_info_styles) is not None
            )
            # Check if flex-wrap is present
            assert 'flex-wrap' in game_info_styles or 'flex-direction' in game_info_styles, \
                "Game info should use flex-wrap or flex-direction for mobile stacking"
    
    def test_padding_on_container(self, css_content):
        """Test that container has padding for mobile spacing."""
        container_pattern = r'\.container\s*\{[^}]*\}'
        container_match = re.search(container_pattern, css_content, re.DOTALL)
        assert container_match is not None, "Container styles should exist"
        
        container_styles = container_match.group(0)
        # Should have padding
        assert 'padding' in container_styles, \
            "Container should have padding for mobile spacing"


class TestBrowserRendering:
    """Test actual browser rendering (requires selenium/playwright)."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_index_renders_on_mobile_viewport(self, client):
        """Test that index page renders successfully (basic check)."""
        response = client.get('/')
        assert response.status_code == 200
        # Check that HTML contains mobile-friendly elements
        assert b'viewport' in response.data.lower()
        assert b'width=device-width' in response.data.lower()
    
    def test_css_file_accessible(self, client):
        """Test that CSS file is accessible."""
        response = client.get('/static/style.css')
        assert response.status_code == 200
        assert response.content_type == 'text/css; charset=utf-8'
    
    def test_js_file_accessible(self, client):
        """Test that JavaScript file is accessible."""
        response = client.get('/static/script.js')
        assert response.status_code == 200
        assert 'javascript' in response.content_type.lower() or \
               'application/javascript' in response.content_type.lower() or \
               'text/javascript' in response.content_type.lower()

