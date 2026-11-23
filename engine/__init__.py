"""Survey-to-book engine.

Converts survey answers into a book: one page per answer, generated
sequentially by a local model conditioned on accumulated context
(a structured story bible, a rolling synopsis, and a sliding window
of the most recent pages). Genre-specific behavior is supplied by
genre packs; this package is genre-agnostic.
"""

__version__ = "0.1.0"
