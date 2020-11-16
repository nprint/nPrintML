"""The aggregator package defines concrete subclasses of
`LabelAggregator` for use in training, evaluating and representing the
results of AutoML training on nPrint data.

In general, these classes take a dataframe generated by the label
aggregation step of the nprintML pipeline. It can be used on its own as
long as it receives a dataframe where each row of the dataframe contains
a single sample and the labels for the samples are contained in a
`label` column in the dataframe.

"""
from .base import LabelAggregator  # noqa
