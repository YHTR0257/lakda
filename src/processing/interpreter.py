"""Question interpretation module for enhancing user queries.

Phase 2: Provides prompt templates for Gemini CLI.
This module is minimal in Phase 2 - full question interpretation happens within Gemini CLI.
"""


class QuestionInterpreter:
    """Provides prompt templates for question enhancement.

    In Phase 2, this is a simple utility for prompt template management.
    Gemini CLI handles the actual question interpretation internally.
    """

    @staticmethod
    def get_system_prompt() -> str:
        """Get the default system prompt for Gemini CLI.

        Returns:
            System prompt instructing the LLM how to answer questions
        """
        return """You are a knowledge retrieval assistant that helps users find information from technical documentation.

When answering questions:
1. Search the available documents thoroughly using the MCP tools
2. Provide clear, concise answers based on the retrieved information
3. Always cite your sources by mentioning the document names
4. If information is not available in the documents, clearly state that
5. For ambiguous questions, provide the best possible answer based on available information

Answer in a professional yet friendly tone."""

    @staticmethod
    def enhance_question(question: str, add_instructions: bool = True) -> str:
        """Enhance a user question with additional context.

        Phase 2: Simple passthrough with optional instruction prefix.

        Args:
            question: Original user question
            add_instructions: Whether to add search instructions

        Returns:
            Enhanced question string
        """
        if not add_instructions:
            return question

        return f"""Please search the available documents and answer the following question:

{question}

Remember to cite your sources."""

    @staticmethod
    def get_prompt_for_metadata_generation(document_content: str) -> str:
        """Get prompt for LLM-based metadata generation.

        Used in document processing (FT04) to automatically generate
        Frontmatter metadata for uploaded documents.

        Args:
            document_content: The document text content

        Returns:
            Prompt for metadata generation
        """
        return f"""Analyze the following document and generate appropriate metadata in YAML Frontmatter format.

Include:
- title: Document title
- description: Brief description (1-2 sentences)
- tags: Relevant tags (3-5 keywords)
- domain: Primary domain category (error-handling, architecture, api-guides, business-logic)
- created_date: Today's date

Document content:
```
{document_content[:1000]}...
```

Generate the Frontmatter metadata:"""
