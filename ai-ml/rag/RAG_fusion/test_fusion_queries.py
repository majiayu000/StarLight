"""Offline unit tests for Fusion's query-to-search cell contract.

Run with: python3 ai-ml/rag/RAG_fusion/test_fusion_queries.py
Only the query generator definition and search orchestration cell are evaluated,
with in-memory fakes. No SDK import, client initialization or notebook kernel runs.
"""

import json
from pathlib import Path
from types import SimpleNamespace
import unittest


NOTEBOOK_PATH = Path(__file__).with_name("fusion.ipynb")


def exercise_query_cell(content):
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    sources = ["".join(cell["source"]) for cell in notebook["cells"]
               if cell["cell_type"] == "code"]
    generator, = [source for source in sources
                  if source.startswith("def generate_queries_chatgpt(")]
    search_cell, = [source for source in sources if "all_results = {}" in source]
    completion = SimpleNamespace(choices=[SimpleNamespace(
        message=SimpleNamespace(content=content))])
    completion_calls = []
    search_calls = []
    fusion_calls = []
    documents = {"source-doc": "A deterministic document fixture."}
    fused = {"fused-doc": 1.0}

    def create_completion(**kwargs):
        completion_calls.append(kwargs)
        return completion

    def search(query, all_documents):
        assert all_documents is documents
        search_calls.append(query)
        return {"call-" + str(len(search_calls)): 0.8}

    def fuse(results):
        fusion_calls.append(dict(results))
        return fused

    namespace = {
        "client": SimpleNamespace(chat=SimpleNamespace(
            completions=SimpleNamespace(create=create_completion))),
        "vector_search": search,
        "reciprocal_rank_fusion": fuse,
        "generate_output": lambda results, queries: (results, queries),
        "all_documents": documents,
    }
    exec(compile(generator, str(NOTEBOOK_PATH) + ":generator", "exec"), namespace)
    namespace["generated_queries"] = namespace["generate_queries_chatgpt"](
        "impact of climate change")
    exec(compile(search_cell, str(NOTEBOOK_PATH) + ":search", "exec"), namespace)
    return completion_calls, search_calls, fusion_calls, namespace["final_output"]


class FusionQueryTests(unittest.TestCase):
    def assert_queries(self, content, expected):
        completion_calls, calls, fusion_calls, output = exercise_query_cell(content)
        self.assertEqual(len(completion_calls), 1)
        self.assertIn("impact of climate change", str(completion_calls[0]["messages"]))
        self.assertEqual(calls, expected)
        expected_results = {
            query: {"call-" + str(index): 0.8}
            for index, query in enumerate(expected, start=1)
        }
        self.assertEqual(fusion_calls, [expected_results])
        self.assertEqual(output, ({"fused-doc": 1.0}, expected))

    def test_numbered_completion_preserves_four_full_queries(self):
        self.assert_queries(
            "1. How does climate change impact biodiversity?\n"
            "2. What are the economic consequences of climate change?\n"
            "3. What are the health effects of climate change?\n"
            "4. How does climate change impact food production?",
            ["1. How does climate change impact biodiversity?",
             "2. What are the economic consequences of climate change?",
             "3. What are the health effects of climate change?",
             "4. How does climate change impact food production?"],
        )

    def test_blank_lines_and_crlf_do_not_become_queries(self):
        self.assert_queries(
            "\r\n  climate and health  \r\n\t\r\nclimate and food\r\n"
            " climate and water \r\nclimate and homes\r\n",
            ["climate and health", "climate and food", "climate and water",
             "climate and homes"],
        )

    def test_unicode_queries_keep_internal_spaces_and_repeated_characters(self):
        self.assert_queries(
            "气候变化与健康\n气候变化与粮食\nclimate  change, climate policy\nété et climat",
            ["气候变化与健康", "气候变化与粮食",
             "climate  change, climate policy", "été et climat"],
        )

    def test_whitespace_only_completion_does_not_search(self):
        self.assert_queries(" \n\t\r\n", [])


if __name__ == "__main__":
    unittest.main()
