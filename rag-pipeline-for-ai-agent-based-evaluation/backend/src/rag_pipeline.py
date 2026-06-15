from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List, Optional
from interface import (
    BaseDatastore,
    BaseIndexer,
    BaseRetriever,
    BaseResponseGenerator,
    BaseEvaluator,
    EvaluationResult,
)


@dataclass
class RAGPipeline:
    """Main RAG pipeline that orchestrates all components."""

    datastore: BaseDatastore
    indexer: BaseIndexer
    retriever: BaseRetriever
    response_generator: BaseResponseGenerator
    evaluator: Optional[BaseEvaluator] = None

    def reset(self) -> None:
        self.datastore.reset()

    def add_documents(self, documents: List[str]) -> None:
        items = self.indexer.index(documents)
        self.datastore.add_items(items)
        print(f"✅ Added {len(items)} items to the datastore.")

    def process_query(self, query: str) -> str:
        search_results = self.retriever.search(query)
        return self.response_generator.generate_response(query, search_results)

    def evaluate(self, sample_questions: List[Dict[str, str]]) -> List[EvaluationResult]:
        questions = [item["question"] for item in sample_questions]
        expected_answers = [item["answer"] for item in sample_questions]
        with ThreadPoolExecutor(max_workers=5) as executor:
            results: List[EvaluationResult] = list(
                executor.map(self._evaluate_single_question, questions, expected_answers)
            )
        return results

    def _evaluate_single_question(self, question: str, expected_answer: str) -> EvaluationResult:
        response = self.process_query(question)
        return self.evaluator.evaluate(question, response, expected_answer)
