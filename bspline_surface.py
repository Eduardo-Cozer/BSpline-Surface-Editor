import numpy as np

class BSplineSurface:
    def __init__(self, m, n, seed=1111):
        self.m = m
        self.n = n
        self.seed = seed
        self.cm = self._generate_control_matrix()
        self.cmSize = self.cm.shape
        self.nI = self.cmSize[0] - 1
        self.nJ = self.cmSize[1] - 1

    def _generate_control_matrix(self):
        np.random.seed(self.seed)
        control_matrix = np.zeros((self.m, self.n, 3))
        for i in range(self.m):
            for j in range(self.n):
                control_matrix[i, j] = [i, j, np.random.randint(0, 10000) / 5000.0 - 1]
        return control_matrix

    def interpolate(self, resolutionI, resolutionJ, orderI, orderJ):
        om = np.zeros(shape=(resolutionI, resolutionJ, 3), dtype=float)

        incrementI = (self.nI - orderI + 2) / float(resolutionI - 1)
        incrementJ = (self.nJ - orderJ + 2) / float(resolutionJ - 1)

        knotsI = self._calcSplineKnots(self.nI, orderI)
        knotsJ = self._calcSplineKnots(self.nJ, orderJ)

        intervalI = 0
        for i in range(resolutionI - 1):
            intervalJ = 0
            for j in range(resolutionJ - 1):
                cP = np.array([0.0, 0.0, 0.0])
                for ki in range(self.cmSize[0]):
                    for kj in range(self.cmSize[1]):
                        bi = self._calcSplineBlend(ki, orderI, knotsI, intervalI)
                        bj = self._calcSplineBlend(kj, orderJ, knotsJ, intervalJ)
                        cP += bi * bj * self.cm[ki, kj]
                om[i, j] = cP
                intervalJ += incrementJ
            intervalI += incrementI

        intervalI = 0
        for i in range(resolutionI - 1):
            cP = np.array([0.0, 0.0, 0.0])
            for ki in range(self.cmSize[0]):
                bi = self._calcSplineBlend(ki, orderI, knotsI, intervalI)
                cP += bi * self.cm[ki, self.nJ]
            om[i, resolutionJ - 1] = cP
            intervalI += incrementI

        om[resolutionI - 1, resolutionJ - 1] = self.cm[self.nI, self.nJ]

        intervalJ = 0
        for j in range(resolutionJ - 1):
            cP = np.array([0.0, 0.0, 0.0])
            for kj in range(self.cmSize[1]):
                bj = self._calcSplineBlend(kj, orderJ, knotsJ, intervalJ)
                cP += bj * self.cm[self.nI, kj]
            om[resolutionI - 1, j] = cP
            intervalJ += incrementJ

        om[resolutionI - 1, resolutionJ - 1] = self.cm[self.nI, self.nJ]

        return om

    def _calcSplineKnots(self, numControlPoints, order):
        totalKnots = numControlPoints + order + 1
        knots = np.zeros(totalKnots, dtype=float)
        for i in range(totalKnots):
            if i < order:
                knots[i] = 0
            elif i <= numControlPoints:
                knots[i] = i - order + 1
            else:
                knots[i] = numControlPoints - order + 2
        return knots

    def _calcSplineBlend(self, k, order, knots, v):
        if order == 1:
            if knots[k] <= v < knots[k + 1]:
                return 1.0
            else:
                return 0.0
        else:
            if knots[k + order - 1] == knots[k] and knots[k + order] == knots[k + 1]:
                return 0.0
            elif knots[k + order - 1] == knots[k]:
                return (knots[k + order] - v) / (knots[k + order] - knots[k + 1]) * self._calcSplineBlend(k + 1, order - 1, knots, v)
            elif knots[k + order] == knots[k + 1]:
                return (v - knots[k]) / (knots[k + order - 1] - knots[k]) * self._calcSplineBlend(k, order - 1, knots, v)
            else:
                term1 = (v - knots[k]) / (knots[k + order - 1] - knots[k]) * self._calcSplineBlend(k, order - 1, knots, v)
                term2 = (knots[k + order] - v) / (knots[k + order] - knots[k + 1]) * self._calcSplineBlend(k + 1, order - 1, knots, v)
                return term1 + term2