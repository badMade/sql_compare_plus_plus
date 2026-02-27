"""Unit tests for sql_compare logic."""
import os
import sys
import unittest

# Ensure we can import sql_compare from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# pylint: disable=wrong-import-position
from sql_compare import (
    strip_sql_comments,
    collapse_whitespace,
    uppercase_outside_quotes,
    remove_outer_parentheses,
    normalize_sql,
    canonicalize_select_list,
    canonicalize_where_and,
    canonicalize_joins,
    compare_sql
)


class TestSQLCompare(unittest.TestCase):
    """Tests for SQL normalization and canonicalization."""

    def test_collapse_whitespace(self):
        """Test whitespace collapsing."""
        self.assertEqual(collapse_whitespace("SELECT  *   FROM   t"), "SELECT * FROM t")
        self.assertEqual(collapse_whitespace("  hello   world  "), "hello world")
        self.assertEqual(collapse_whitespace("no_extra_spaces"), "no_extra_spaces")
        self.assertEqual(collapse_whitespace("a\t\tb\n\nc"), "a b c")
        self.assertEqual(collapse_whitespace(""), "")

    def test_strip_comments(self):
        """Test comment stripping."""
        sql = "SELECT * FROM t -- comment\n WHERE x=1 /* block */"
        # strip_sql_comments removes comments but leaves newlines/whitespace often
        expected_part = "SELECT * FROM t \n WHERE x=1 "
        self.assertEqual(strip_sql_comments(sql), expected_part)

    def test_uppercase_outside_quotes(self):
        """Test uppercasing outside of quotes."""
        sql = "select 'abc' as \"def\", [ghi]"
        expected = "SELECT 'abc' AS \"def\", [ghi]"
        self.assertEqual(uppercase_outside_quotes(sql), expected)

    def test_remove_outer_parentheses(self):
        """Test removal of outer parentheses."""
        self.assertEqual(remove_outer_parentheses("(SELECT 1)"), "SELECT 1")
        self.assertEqual(remove_outer_parentheses("((SELECT 1))"), "SELECT 1")
        # Should not remove if not fully enclosing
        self.assertEqual(remove_outer_parentheses(
            "(SELECT 1) UNION (SELECT 2)"), "(SELECT 1) UNION (SELECT 2)")

    def test_normalize_sql(self):
        """Test the full normalization pipeline."""
        sql = "select a, b from t; -- comment"
        # Uppercased, no semi, no comment, collapsed ws
        expected = "SELECT A, B FROM T"
        self.assertEqual(normalize_sql(sql), expected)

    def test_canonicalize_select_list(self):
        """Test canonicalization of SELECT list."""
        # Note: canonicalize_select_list expects uppercase keywords (SELECT, FROM)
        # to function correctly because top_level_find_kw is case-sensitive.
        sql = "SELECT b, a FROM t"
        expected = "SELECT a, b FROM t"
        self.assertEqual(canonicalize_select_list(sql), expected)

    def test_canonicalize_where(self):
        """Test canonicalization of WHERE..AND clauses."""
        sql = "SELECT * FROM t WHERE y=2 AND x=1"
        expected = "SELECT * FROM t WHERE x=1 AND y=2"
        self.assertEqual(canonicalize_where_and(sql), expected)

    def test_canonicalize_joins_inner(self):
        """Test canonicalization of simple INNER JOINs."""
        # canonicalize_joins expects uppercase FROM.
        sql = "SELECT * FROM t1 JOIN t3 ON t1.id=t3.id JOIN t2 ON t1.id=t2.id"
        # t2 comes before t3 alphabetically
        expected = "SELECT * FROM t1 JOIN t2 ON t1.id=t2.id JOIN t3 ON t1.id=t3.id"
        self.assertEqual(canonicalize_joins(sql), expected)

    def test_canonicalize_joins_mixed(self):
        """Test canonicalization of mixed reorderable and non-reorderable JOINs."""
        # INNER then LEFT. LEFT breaks the run of reorderable inner joins.
        sql = "SELECT * FROM t1 JOIN t3 ON x JOIN t2 ON y LEFT JOIN t4 ON z"
        # t3 and t2 reorder. t4 stays.
        expected = "SELECT * FROM t1 JOIN t2 ON y JOIN t3 ON x LEFT JOIN t4 ON z"
        self.assertEqual(canonicalize_joins(sql), expected)

    def test_canonicalize_joins_left_enabled(self):
        """Test canonicalization of LEFT JOINs when enabled."""
        sql = "SELECT * FROM t1 LEFT JOIN t3 ON x LEFT JOIN t2 ON y"
        # Default: no reorder left
        self.assertEqual(canonicalize_joins(sql), sql)
        # Enabled
        expected = "SELECT * FROM t1 LEFT JOIN t2 ON y LEFT JOIN t3 ON x"
        self.assertEqual(canonicalize_joins(sql, allow_left=True), expected)

    def test_full_comparison(self):
        """Test the full compare_sql function for a canonical match."""
        s1 = "select a,b from t where x=1 and y=2"
        s2 = "SELECT b, a FROM t WHERE y=2 AND x=1;"
        res = compare_sql(s1, s2, enable_join_reorder=True)
        self.assertTrue(res["canonical_equal"])
        self.assertFalse(res["exact_equal"])  # Tokens differ (order)
        self.assertIn("timestamp", res)

    def test_complex_join_reorder(self):
        """Test a more complex JOIN reordering scenario."""
        # A complex case: INNER, INNER, LEFT, INNER, FULL
        # INNER/INNER reorder.
        # LEFT breaks.
        # INNER (single) stays.
        # FULL breaks.
        sql = ("SELECT * FROM t "
               "JOIN c ON c.id=t.id "
               "JOIN b ON b.id=t.id "
               "LEFT JOIN d ON d.id=t.id "
               "JOIN e ON e.id=t.id")
        # b < c.
        expected = ("SELECT * FROM t "
                    "JOIN b ON b.id=t.id "
                    "JOIN c ON c.id=t.id "
                    "LEFT JOIN d ON d.id=t.id "
                    "JOIN e ON e.id=t.id")
        self.assertEqual(canonicalize_joins(sql), expected)


if __name__ == '__main__':
    unittest.main()
