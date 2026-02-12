"""
Unit tests for apps/core/seo.py

Tests JSON-LD security and structure validation.
These tests validate FIX C-2: proper escaping of </script> tags in JSON-LD output.
No database access required - uses simple dicts and mock objects.
"""

from types import SimpleNamespace

import pytest

from apps.core.seo import JsonLdMixin, _json_ld_script


# ---------------------------------------------------------------------------
# JSON-LD Security Tests (CRITICAL - validates FIX C-2)
# ---------------------------------------------------------------------------


class TestJsonLdScript:
    """Tests for _json_ld_script function."""

    def test_json_ld_script_escapes_closing_script_tag(self):
        """Test that </script> in data becomes <\\/script> to prevent XSS."""
        data = {
            "@type": "Article",
            "name": "Test</script><script>alert('XSS')</script>",
        }

        result = _json_ld_script(data)

        # The </script> tag must be escaped to prevent breaking out of JSON-LD
        assert "</script>" not in result.replace("</script>", "")  # Allow the closing tag
        assert "<\\/script>" in result
        assert "Test<\\/script><script>alert('XSS')<\\/script>" in result

    def test_json_ld_script_adds_context(self):
        """Test that @context is added if missing."""
        data = {
            "@type": "WebPage",
            "name": "Test Page",
        }

        result = _json_ld_script(data)

        assert '"@context":"https://schema.org"' in result or '"@context": "https://schema.org"' in result

    def test_json_ld_script_preserves_existing_context(self):
        """Test that existing @context is not overwritten."""
        data = {
            "@context": "https://custom.schema.org",
            "@type": "CustomType",
            "name": "Custom Item",
        }

        result = _json_ld_script(data)

        assert "https://custom.schema.org" in result
        # Should not contain the default context
        assert result.count("@context") == 1

    def test_json_ld_script_empty_data_returns_empty(self):
        """Test that None, empty dict, or False returns empty string."""
        assert _json_ld_script(None) == ""
        assert _json_ld_script({}) == ""
        assert _json_ld_script(False) == ""

    def test_json_ld_script_unicode_preserved(self):
        """Test that Unicode characters are not escaped (ensure_ascii=False)."""
        data = {
            "@type": "Organization",
            "name": "Club Motociclisti Milano",
            "description": "The finest club in Italia for motorcycle ensusiasts.",
        }

        result = _json_ld_script(data)

        # Unicode chars should be preserved, not escaped to \\uXXXX
        assert "Milano" in result
        assert "Italia" in result
        # These accented chars should NOT be escaped
        assert "\\u" not in result or "\\u" in result.replace('\\"', "")

    def test_json_ld_script_unicode_special_chars(self):
        """Test that special Unicode characters like emojis and accents are preserved."""
        data = {
            "@type": "Event",
            "name": "Raduno Estivo",
            "location": "Piazza Duomo, Milano",
        }

        result = _json_ld_script(data)

        # Accented characters preserved
        assert "Piazza Duomo" in result
        assert "Milano" in result

    def test_json_ld_script_nested_closing_tags(self):
        """Test multiple </script>, </style> etc in nested fields."""
        data = {
            "@type": "Article",
            "name": "Article with </script> tag",
            "description": "Contains </style> and </script> and </iframe>",
            "author": {
                "@type": "Person",
                "name": "Author</script>Name",
            },
            "keywords": ["tag1", "tag2</script>", "</style>tag3"],
        }

        result = _json_ld_script(data)

        # All closing tags with / should be escaped
        # The result should not contain any unescaped </
        # Split by the actual closing </script> tag of the JSON-LD wrapper
        json_content = result.split('type="application/ld+json">')[1].split("</script>")[0]
        assert "</" not in json_content  # No unescaped closing tags in JSON data
        assert "<\\/" in json_content  # Escaped versions exist

    def test_json_ld_script_structure(self):
        """Test that output has correct script tag structure."""
        data = {
            "@type": "WebPage",
            "name": "Test",
        }

        result = _json_ld_script(data)

        assert result.startswith('<script type="application/ld+json">')
        assert result.endswith("</script>")


# ---------------------------------------------------------------------------
# JsonLdMixin Tests
# ---------------------------------------------------------------------------


class MockPage(JsonLdMixin):
    """Mock page class for testing JsonLdMixin."""

    def __init__(self, title="Test Page", json_ld_data=None):
        self.title = title
        self._json_ld_data = json_ld_data

    def get_json_ld(self):
        if self._json_ld_data is not None:
            return self._json_ld_data
        return super().get_json_ld()


class TestJsonLdMixin:
    """Tests for JsonLdMixin class."""

    def test_json_ld_mixin_escapes_closing_script(self):
        """Test that JsonLdMixin.get_json_ld_script escapes </script> tags."""
        page = MockPage(
            title="Test",
            json_ld_data={
                "@type": "Article",
                "name": "Malicious</script><script>alert(1)</script>Content",
            },
        )

        result = page.get_json_ld_script()

        # Convert SafeString to regular string for testing
        result_str = str(result)

        # The </script> inside the JSON data must be escaped
        assert "<\\/script>" in result_str
        # The actual closing </script> tag for the JSON-LD wrapper should exist
        assert result_str.endswith("</script>")

    def test_json_ld_mixin_adds_context(self):
        """Test that JsonLdMixin adds @context if missing."""
        page = MockPage(
            title="Test Page",
            json_ld_data={
                "@type": "WebPage",
                "name": "My Page",
            },
        )

        result = str(page.get_json_ld_script())

        assert "https://schema.org" in result

    def test_json_ld_mixin_preserves_context(self):
        """Test that JsonLdMixin preserves existing @context."""
        page = MockPage(
            title="Test",
            json_ld_data={
                "@context": "https://my-custom-schema.org",
                "@type": "CustomType",
            },
        )

        result = str(page.get_json_ld_script())

        assert "https://my-custom-schema.org" in result

    def test_json_ld_mixin_empty_data_returns_empty(self):
        """Test that None from get_json_ld returns empty string."""
        page = MockPage(title="Test", json_ld_data=None)
        # Override to return None
        page.get_json_ld = lambda: None

        result = page.get_json_ld_script()

        assert result == ""

    def test_json_ld_mixin_default_implementation(self):
        """Test the default get_json_ld implementation."""
        page = MockPage(title="My Awesome Page")
        # Don't override, use default

        page._json_ld_data = None  # Use default behavior
        result = page.get_json_ld()

        assert result["@type"] == "WebPage"
        assert result["name"] == "My Awesome Page"

    def test_json_ld_mixin_unicode_preserved(self):
        """Test that Unicode is preserved in JsonLdMixin output."""
        page = MockPage(
            title="Test",
            json_ld_data={
                "@type": "Event",
                "name": "Festa della Repubblica",
                "location": "Roma, Italia",
            },
        )

        result = str(page.get_json_ld_script())

        assert "Festa della Repubblica" in result
        assert "Roma" in result
        assert "Italia" in result


# ---------------------------------------------------------------------------
# Edge Case Tests
# ---------------------------------------------------------------------------


class TestJsonLdEdgeCases:
    """Edge case tests for JSON-LD functions."""

    def test_deeply_nested_script_tags(self):
        """Test escaping in deeply nested structures."""
        data = {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "item": {
                        "@type": "Article",
                        "name": "Nested</script>Content",
                        "author": {
                            "@type": "Person",
                            "bio": "Bio with </script> tag",
                        },
                    },
                },
            ],
        }

        result = _json_ld_script(data)
        json_content = result.split('type="application/ld+json">')[1].split("</script>")[0]

        # No unescaped closing tags
        assert "</" not in json_content

    def test_all_html_closing_tags_escaped(self):
        """Test that all HTML-like closing tags are escaped."""
        data = {
            "@type": "WebPage",
            "content": "</div></span></p></a></img></script></style>",
        }

        result = _json_ld_script(data)
        json_content = result.split('type="application/ld+json">')[1].split("</script>")[0]

        # All </ patterns should be escaped to <\/
        assert "</" not in json_content
        assert "<\\/div>" in json_content
        assert "<\\/span>" in json_content
        assert "<\\/script>" in json_content
        assert "<\\/style>" in json_content

    def test_mixed_content_with_script_tags(self):
        """Test real-world scenario with mixed HTML-like content."""
        data = {
            "@type": "Article",
            "articleBody": """
                This article discusses <code>function()</code> usage.
                Warning: Never trust input like </script><script>evil()</script>.
                Use proper escaping!
            """,
        }

        result = _json_ld_script(data)
        json_content = result.split('type="application/ld+json">')[1].split("</script>")[0]

        # Verify the XSS vector is neutralized
        assert "</script>" not in json_content
        assert "<\\/script>" in json_content
