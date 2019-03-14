"""Gaussian Process Regression model."""

import logging
import os
from pprint import pformat

import numpy as np
from esmvaltool.diag_scripts.mlr.models import MLRModel
from george import GP
from scipy.optimize import fmin_l_bfgs_b
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.exceptions import NotFittedError
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.utils import check_random_state
from sklearn.utils.validation import check_array, check_X_y

logger = logging.getLogger(os.path.basename(__file__))


@MLRModel.register_mlr_model('sklearn_gpr')
class SklearnGPRModel(MLRModel):
    """Gaussian Process Regression model (:mod:`sklearn` implementation).

    Note
    ----
    See :mod:`esmvaltool.diag_scripts.mlr.models`.

    """

    _CLF_TYPE = GaussianProcessRegressor

    def print_kernel_info(self):
        """Print information of the fitted kernel of the GPR model."""
        if not self._is_fitted():
            logger.error("Printing kernel not possible because the model is "
                         "not fitted yet, call fit() first")
            return
        kernel = self._clf.named_steps['regressor'].regressor_.kernel_
        logger.info("Fitted kernel: %s (%i hyperparameters)", kernel,
                    kernel.n_dims)
        logger.info("Hyperparameters:")
        for hyper_param in kernel.hyperparameters:
            logger.info(hyper_param)
        logger.info("Theta:")
        for elem in kernel.theta:
            logger.info(elem)


class GeorgeGaussianProcessRegressor(BaseEstimator, RegressorMixin):
    """:mod:`sklearn` API for :mod:`george.GP`.

    Note
    ----
    :mod:`george` offers faster optimization functions useful for large data
    sets. The implementation of this class is based on :mod:`sklearn`
    <https://scikit-learn.org/stable/modules/generated/
    sklearn.gaussian_process.GaussianProcessRegressor.html>.

    """

    _SKLEARN_SEP = '__'
    _GEORGE_SEP = ':'

    def __init__(self,
                 kernel=None,
                 fit_kernel=True,
                 mean=None,
                 fit_mean=None,
                 white_noise=None,
                 fit_white_noise=None,
                 solver=None,
                 optimizer='fmin_l_bfgs_b',
                 n_restarts_optimizer=0,
                 copy_X_train=True,
                 random_state=None,
                 **kwargs):
        """Initialize :mod:`george.GP` object.

        Note
        ----
        See <https://george.readthedocs.io/en/latest/user/gp/>.

        """
        self.kernel = kernel
        self.fit_kernel = fit_kernel
        self.mean = mean
        self.fit_mean = fit_mean
        self.white_noise = white_noise
        self.fit_white_noise = fit_white_noise
        self.solver = solver
        self.optimizer = optimizer
        self.n_restarts_optimizer = n_restarts_optimizer
        self.copy_X_train = copy_X_train
        self.random_state = random_state
        self.kwargs = kwargs
        self._gp = None
        self._init_gp()

        # Training data
        self._x_train = None
        self._y_train = None

        # Random number generator
        self._rng = check_random_state(self.random_state)

    def fit(self, x_train, y_train):
        """Fit regressor using given training data."""
        (x_train, y_train) = check_X_y(
            x_train, y_train, multi_output=True, y_numeric=True)
        self._x_train = np.copy(x_train) if self.copy_X_train else x_train
        self._y_train = np.copy(y_train) if self.copy_X_train else y_train
        self._gp.compute(self._x_train)

        # Optimize hyperparameters of kernel if desired
        if self.optimizer is None:
            logger.warning(
                "No optimizer for optimizing Gaussian Process (kernel) "
                "hyperparameters specified, using initial values")
            return self
        if not self._gp.vector_size:
            logger.warning(
                "No hyperparameters for Gaussian Process (kernel) specified, "
                "optimization not possible")
            return self

        # Objective function to minimize (negative log-marginal likelihood)
        def obj_func(theta, eval_gradient=True):
            self._gp.set_parameter_vector(theta)
            log_like = self._gp.log_likelihood(self._y_train, quiet=True)
            log_like = log_like if np.isfinite(log_like) else -np.inf
            if eval_gradient:
                grad_log_like = self._gp.grad_log_likelihood(
                    self._y_train, quiet=True)
                return (-log_like, -grad_log_like)
            return -log_like

        # Start optimization from values specfied in kernel
        logger.info("Optimizing george GP hyperparameters")
        logger.info(pformat(self.get_george_params()))
        bounds = self._gp.get_parameter_bounds()
        optima = [
            self._constrained_optimization(obj_func,
                                           self._gp.get_parameter_vector(),
                                           bounds)
        ]

        # Additional runs (chosen from log-uniform intitial theta)
        if self.n_restarts_optimizer > 0:
            if any([None in b for b in bounds]):
                logger.error(
                    "Multiple optimizer restarts (n_restarts_optimizer > 0) "
                    "require that all bounds are given and finite (not set to "
                    "'None')")
            elif not np.isfinite(bounds).all():
                logger.error(
                    "Multiple optimizer restarts (n_restarts_optimizer > 0) "
                    "require that all bounds are finite")
            else:
                for idx in range(self.n_restarts_optimizer):
                    logger.info(
                        "Restarted hyperparameter optimization, "
                        "iteration %3i/%i", idx + 1, self.n_restarts_optimizer)
                    theta_initial = self._rng.uniform(bounds[:, 0],
                                                      bounds[:, 1])
                    optima.append(
                        self._constrained_optimization(obj_func, theta_initial,
                                                       bounds))

        # Select best run (with lowest negative log-marginal likelihood)
        log_like_vals = [opt[1] for opt in optima]
        theta_opt = optima[np.argmin(log_like_vals)][0]
        self._gp.set_parameter_vector(theta_opt)
        self._gp.compute(self._x_train)
        logger.info("Result of hyperparameter optimization:")
        logger.info(pformat(self.get_george_params()))
        return self

    def get_george_params(self, include_frozen=False, prefix=''):
        """Get `dict` of parameters of the :mod:`george.GP` class member."""
        params = self._gp.get_parameter_dict(include_frozen=include_frozen)
        new_params = {}
        for (key, val) in params.items():
            key = self._str_to_sklearn(key)
            new_params[f'{prefix}{key}'] = val
        return new_params

    def predict(self, x_pred, **kwargs):
        """Predict for unknown data."""
        if not self._gp.computed:
            raise NotFittedError("Prediction not possible, model not fitted")
        x_pred = check_array(x_pred)
        return self._gp.predict(self._y_train, x_pred, **kwargs)

    def set_params(self, **params):
        """Set the parameters of this estimator."""
        valid_gp_params = self._gp.get_parameter_names(include_frozen=True)
        gp_params = {}
        remaining_params = {}
        for (key, val) in params.items():
            new_key = self._str_to_george(key)
            if new_key in valid_gp_params:
                gp_params[new_key] = val
            else:
                remaining_params[key] = val

        # Initialize new GP object and update parameters of this class
        if remaining_params:
            logger.debug("Updating <%s> with parameters %s",
                         self.__class__.__name__, remaining_params)
            super().set_params(**remaining_params)
            self._init_gp()

        # Update parameters of GP member
        valid_gp_params = self._gp.get_parameter_names(include_frozen=True)
        for (key, val) in gp_params.items():
            if key in valid_gp_params:
                self._gp.set_parameter(key, val)
                logger.debug("Set parameter '%s' of george GP member to '%s'",
                             self._str_to_sklearn(key), val)
            else:
                logger.error(
                    "Parameter '%s' is not a valid parameter of the GP member "
                    "anymore, it was removed after new initialization with "
                    "other parameters", self._str_to_sklearn(key))
        return self

    def _constrained_optimization(self, obj_func, initial_theta, bounds):
        """Optimize hyperparameters.

        Note
        ----
        See implementation of :mod:`sklearn.gaussian_process.
        GaussianProcessRegressor`.

        """
        if self.optimizer == 'fmin_l_bfgs_b':
            (theta_opt, func_min, convergence_dict) = fmin_l_bfgs_b(
                obj_func, initial_theta, bounds=bounds)
            if convergence_dict["warnflag"] != 0:
                logger.warning(
                    "fmin_l_bfgs_b terminated abnormally with the state: %s",
                    convergence_dict)
        elif callable(self.optimizer):
            (theta_opt, func_min) = self.optimizer(
                obj_func, initial_theta, bounds=bounds)
        else:
            raise ValueError(f"Unknown optimizer {self.optimizer}")
        return (theta_opt, func_min)

    def _init_gp(self):
        """Initialize :mod:`george.GP` instance."""
        self._gp = GP(
            kernel=self.kernel,
            fit_kernel=self.fit_kernel,
            mean=self.mean,
            fit_mean=self.fit_mean,
            white_noise=self.white_noise,
            fit_white_noise=self.fit_white_noise,
            solver=self.solver,
            **self.kwargs)
        logger.debug("Initialized george GP member of <%s>",
                     self.__class__.__name__)

    @classmethod
    def _str_to_george(cls, string):
        """Convert seperators of parameter string to :mod:`george`."""
        return string.replace(cls._SKLEARN_SEP, cls._GEORGE_SEP)

    @classmethod
    def _str_to_sklearn(cls, string):
        """Convert seperators of parameter string to :mod:`sklearn`."""
        return string.replace(cls._GEORGE_SEP, cls._SKLEARN_SEP)


@MLRModel.register_mlr_model('george_gpr')
class GeorgeGPRModel(MLRModel):
    """Gaussian Process Regression model (:mod:`george` implementation).

    Note
    ----
    See :mod:`esmvaltool.diag_scripts.mlr.models`.

    """

    _CLF_TYPE = GeorgeGaussianProcessRegressor
    _GEORGE_CLF = True

    def print_kernel_info(self):
        """Print information of the fitted kernel of the GPR model."""
        logger.error("PRINTING KERNEL NOT SUPPORTED YET")
