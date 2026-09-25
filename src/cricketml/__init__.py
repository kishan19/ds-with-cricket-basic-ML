"""cricketml — machine learning fundamentals, taught through cricket.

The package holds the *shared* machinery every lesson reuses: paths, the random
seed, data loading, leakage-safe splits, metrics and the plot theme. Lesson
notebooks import from here so that no two lessons disagree about how a model is
validated or how a chart looks.
"""

from cricketml.config import PATHS, SEED

__all__ = ["PATHS", "SEED", "__version__"]
__version__ = "0.1.0"
