import random
import abc


def create_basic_distribution():
    return _BasicDistribution(random.Random())


def create_squared_distribution():
    """Creates a distribution where items with higher weight are given even more weight.

    This is done by squaring the weight of newly-added items.

    For example, if one item is added with weight 1 and another item is added with weight
    3, then in a basic distribution, the first item has a 25% chance of being selected from
    the distribution. However, squaring the weights first gives 1^2 = 1 and 3^2 = 9, so
    the first item now has only a 10% chance of being selected.
    """
    return _SquaredDistribution(random.Random())


class _BaseDistribution:

    def __init__(self, r):
        self._r = r
        self._item_weight_pairs = []
        self._total_weight = 0

    def add(self, item, weight):
        if weight > 0:
            modified_weight = self._calculate_modified_weight(weight)
            self._item_weight_pairs.append((item, modified_weight))
            self._total_weight += modified_weight

    @abc.abstractmethod
    def _calculate_modified_weight(self, weight):
        pass

    def get_random(self):
        if not self._item_weight_pairs:
            return None

        floating_point_index = self._r.uniform(0, self._total_weight)
        weight_sum = 0
        for item, weight in self._item_weight_pairs:
            weight_sum += weight
            if floating_point_index <= weight_sum:
                return item

        raise AssertionError("Something should always be returned from a non-empty distribution!")


class _BasicDistribution(_BaseDistribution):

    def __init__(self, r):
        super().__init__(r)

    def _calculate_modified_weight(self, weight):
        return weight


class _SquaredDistribution(_BaseDistribution):
    def __init__(self, r):
        super().__init__(r)

    def _calculate_modified_weight(self, weight):
        return weight * weight
