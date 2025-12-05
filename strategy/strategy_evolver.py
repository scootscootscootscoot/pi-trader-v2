"""
Strategy evolution system for trading bot.

This module provides performance-based strategy evolution capabilities,
including prompt adjustment based on trading outcomes and version control
for strategy improvements.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import hashlib
from collections import defaultdict
import copy

logger = logging.getLogger(__name__)


@dataclass
class StrategyVersion:
    """Represents a version of a trading strategy."""

    version_id: str
    timestamp: datetime
    prompt_template: str
    strategy_params: Dict[str, Any]
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    parent_version: Optional[str] = None
    change_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'version_id': self.version_id,
            'timestamp': self.timestamp.isoformat(),
            'prompt_template': self.prompt_template,
            'strategy_params': self.strategy_params,
            'performance_metrics': self.performance_metrics,
            'parent_version': self.parent_version,
            'change_reason': self.change_reason
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyVersion':
        """Create instance from dictionary."""
        return cls(
            version_id=data['version_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            prompt_template=data['prompt_template'],
            strategy_params=data['strategy_params'],
            performance_metrics=data['performance_metrics'],
            parent_version=data['parent_version'],
            change_reason=data['change_reason']
        )


@dataclass
class PerformanceRecord:
    """Tracks performance of a strategy version."""

    version_id: str
    trades_executed: int = 0
    profitable_trades: int = 0
    total_profit: float = 0.0
    total_loss: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0
    evaluation_period_days: int = 0

    def add_trade(self, profit: float):
        """Add a trade result to performance record."""
        self.trades_executed += 1

        if profit > 0:
            self.profitable_trades += 1
            self.total_profit += profit
        else:
            self.total_loss += abs(profit)

        self._update_metrics()

    def _update_metrics(self):
        """Update calculated performance metrics."""
        if self.profitable_trades > 0:
            self.average_win = self.total_profit / self.profitable_trades

        losing_trades = self.trades_executed - self.profitable_trades
        if losing_trades > 0:
            self.average_loss = self.total_loss / losing_trades

        self.win_rate = (self.profitable_trades / self.trades_executed) if self.trades_executed > 0 else 0

        if self.total_loss > 0:
            self.profit_factor = self.total_profit / self.total_loss
        else:
            self.profit_factor = float('inf') if self.total_profit > 0 else 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'version_id': self.version_id,
            'trades_executed': self.trades_executed,
            'profitable_trades': self.profitable_trades,
            'total_profit': self.total_profit,
            'total_loss': self.total_loss,
            'average_win': self.average_win,
            'average_loss': self.average_loss,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'max_drawdown': self.max_drawdown,
            'evaluation_period_days': self.evaluation_period_days
        }


class StrategyEvolver:
    """
    Evolves trading strategies based on performance data.

    Manages strategy versioning, performance tracking, and automatic
    prompt adjustments to improve trading outcomes over time.
    """

    def __init__(self, storage_path: str = "data/strategy_versions",
                 current_version_file: str = "data/current_strategy.json"):
        """
        Initialize the strategy evolver.

        Args:
            storage_path: Directory to store strategy versions
            current_version_file: File path for current active strategy
        """
        self.storage_path = storage_path
        self.current_version_file = current_version_file
        self.versions: Dict[str, StrategyVersion] = {}
        self.performance_records: Dict[str, PerformanceRecord] = {}
        self.current_version_id: Optional[str] = None

        # Evolution parameters
        self.min_evaluation_trades = 10
        self.min_evaluation_days = 3
        self.improvement_threshold = 0.05  # 5% improvement required
        self.max_adjustment_factor = 0.2   # Maximum 20% parameter change

        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)

        # Load existing data
        self._load_strategy_versions()
        self._load_current_version()

    def _load_strategy_versions(self):
        """Load strategy versions from storage."""
        if not os.path.exists(self.storage_path):
            return

        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_path, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        version = StrategyVersion.from_dict(data)
                        self.versions[version.version_id] = version

                        # Initialize performance record if it exists
                        if 'performance' in data:
                            perf_data = data['performance']
                            perf_record = PerformanceRecord(**perf_data)
                            self.performance_records[version.version_id] = perf_record

                except Exception as e:
                    logger.warning(f"Failed to load strategy version from {filepath}: {e}")

        logger.info(f"Loaded {len(self.versions)} strategy versions")

    def _load_current_version(self):
        """Load the current active version."""
        if os.path.exists(self.current_version_file):
            try:
                with open(self.current_version_file, 'r') as f:
                    data = json.load(f)
                    self.current_version_id = data.get('version_id')
            except Exception as e:
                logger.warning(f"Failed to load current version: {e}")

    def _save_version(self, version: StrategyVersion, performance_record: Optional[PerformanceRecord] = None):
        """Save a strategy version to storage."""
        data = version.to_dict()
        if performance_record:
            data['performance'] = performance_record.to_dict()

        filename = f"{version.version_id}.json"
        filepath = os.path.join(self.storage_path, filename)

        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved strategy version: {version.version_id}")
        except Exception as e:
            logger.error(f"Failed to save strategy version {version.version_id}: {e}")

    def _save_current_version(self):
        """Save the current active version ID."""
        data = {'version_id': self.current_version_id}

        try:
            with open(self.current_version_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Updated current version: {self.current_version_id}")
        except Exception as e:
            logger.error(f"Failed to save current version: {e}")

    def _generate_version_id(self, prompt_template: str, params: Dict[str, Any],
                           parent_version: Optional[str] = None) -> str:
        """Generate a unique version ID based on content."""
        content = f"{prompt_template}_{json.dumps(params, sort_keys=True)}_{parent_version or ''}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def create_new_strategy_version(self, prompt_template: str,
                                   strategy_params: Dict[str, Any],
                                   parent_version: Optional[str] = None,
                                   change_reason: str = "") -> str:
        """
        Create a new strategy version.

        Args:
            prompt_template: The prompt template being used
            strategy_params: Strategy-specific parameters
            parent_version: Parent version ID if this is an evolution
            change_reason: Reason for the change

        Returns:
            Version ID of the new strategy
        """
        version_id = self._generate_version_id(prompt_template, strategy_params, parent_version)

        # Check if this version already exists
        if version_id in self.versions:
            logger.info(f"Strategy version {version_id} already exists")
            return version_id

        version = StrategyVersion(
            version_id=version_id,
            timestamp=datetime.now(),
            prompt_template=prompt_template,
            strategy_params=strategy_params,
            parent_version=parent_version,
            change_reason=change_reason
        )

        self.versions[version_id] = version

        # Initialize performance record
        self.performance_records[version_id] = PerformanceRecord(version_id)

        # Save to storage
        self._save_version(version, self.performance_records[version_id])

        # Set as current if no current version exists
        if self.current_version_id is None:
            self.current_version_id = version_id
            self._save_current_version()

        logger.info(f"Created new strategy version: {version_id}")
        return version_id

    def record_trade_result(self, profit_loss: float):
        """
        Record the result of a trade for the current strategy version.

        Args:
            profit_loss: Profit/loss amount for the trade (positive = profit)
        """
        if not self.current_version_id:
            logger.warning("No current strategy version set")
            return

        if self.current_version_id not in self.performance_records:
            logger.error(f"No performance record found for version {self.current_version_id}")
            return

        # Add trade to performance record
        self.performance_records[self.current_version_id].add_trade(profit_loss)

        # Update the version's performance metrics in storage
        current_version = self.versions[self.current_version_id]
        current_version.performance_metrics = self.performance_records[self.current_version_id].to_dict()
        self._save_version(current_version, self.performance_records[self.current_version_id])

        logger.debug(f"Recorded trade P/L: {profit_loss} for version {self.current_version_id}")

    def get_strategy_version(self, version_id: Optional[str] = None) -> Optional[StrategyVersion]:
        """
        Get a strategy version by ID.

        Args:
            version_id: Version ID to retrieve (uses current if None)

        Returns:
            StrategyVersion instance or None if not found
        """
        version_id = version_id or self.current_version_id
        if not version_id:
            return None

        return self.versions.get(version_id)

    def get_current_strategy(self) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Get the current strategy template and parameters.

        Returns:
            Tuple of (prompt_template, strategy_params) or (None, None) if not found
        """
        if not self.current_version_id:
            return None, None

        version = self.get_strategy_version(self.current_version_id)
        if not version:
            return None, None

        return version.prompt_template, version.strategy_params

    def evaluate_strategy_evolution(self) -> Optional[str]:
        """
        Evaluate if the current strategy needs evolution based on performance.

        Analyzes recent performance and decides if prompt adjustments
        or template changes would be beneficial.

        Returns:
            New version ID if evolution occurred, None otherwise
        """
        if not self.current_version_id:
            logger.warning("No current strategy version to evaluate")
            return None

        current_perf = self.performance_records.get(self.current_version_id)
        current_version = self.versions.get(self.current_version_id)

        if not current_perf or not current_version:
            logger.warning("Missing performance data for current strategy")
            return None

        # Check if we have enough data for evaluation
        if current_perf.trades_executed < self.min_evaluation_trades:
            logger.info(f"Insufficient trades ({current_perf.trades_executed}) for evaluation. "
                       f"Need at least {self.min_evaluation_trades}")
            return None

        # Get historical performance for comparison
        baseline_perf = self._get_baseline_performance()

        # Decide if evolution is needed
        evolution_needed = self._should_evolve_strategy(current_perf, baseline_perf)

        if not evolution_needed:
            logger.info("Current strategy performance is acceptable, no evolution needed")
            return None

        # Create evolved strategy
        new_prompt, new_params = self._create_evolved_strategy(current_version, current_perf, baseline_perf)

        if new_prompt != current_version.prompt_template or new_params != current_version.strategy_params:
            change_reason = self._generate_change_reason(current_perf, baseline_perf)
            new_version_id = self.create_new_strategy_version(
                new_prompt, new_params, self.current_version_id, change_reason
            )

            # Switch to new version
            self.current_version_id = new_version_id
            self._save_current_version()

            logger.info(f"Evolved strategy to version {new_version_id}: {change_reason}")
            return new_version_id
        else:
            logger.info("Strategy evolution attempted but no changes made")
            return None

    def _get_baseline_performance(self) -> Optional[PerformanceRecord]:
        """Get baseline performance from the most successful recent version."""
        valid_versions = []

        for version_id, perf in self.performance_records.items():
            if perf.trades_executed >= self.min_evaluation_trades:
                valid_versions.append(perf)

        if not valid_versions:
            return None

        # Return the version with best win rate as baseline
        return max(valid_versions, key=lambda p: p.win_rate)

    def _should_evolve_strategy(self, current_perf: PerformanceRecord,
                               baseline_perf: Optional[PerformanceRecord]) -> bool:
        """
        Determine if strategy evolution is warranted.

        Args:
            current_perf: Current strategy performance
            baseline_perf: Baseline performance for comparison

        Returns:
            True if evolution should occur
        """
        # Always consider evolution if we have very poor performance
        if current_perf.win_rate < 0.3 and current_perf.trades_executed >= self.min_evaluation_trades:
            return True

        # If we have a strong baseline, compare against it
        if baseline_perf and current_perf.win_rate < baseline_perf.win_rate * (1 - self.improvement_threshold):
            return True

        # Consider evolution if profit factor is too low
        if current_perf.profit_factor < 1.1:
            return True

        return False

    def _create_evolved_strategy(self, current_version: StrategyVersion,
                                current_perf: PerformanceRecord,
                                baseline_perf: Optional[PerformanceRecord]) -> Tuple[str, Dict[str, Any]]:
        """
        Create an evolved version of the current strategy.

        Args:
            current_version: Current strategy version
            current_perf: Current performance data
            baseline_perf: Baseline performance data

        Returns:
            Tuple of (new_prompt_template, new_strategy_params)
        """
        new_prompt = current_version.prompt_template
        new_params = copy.deepcopy(current_version.strategy_params)

        # Analyze performance to determine what to adjust
        adjustments = self._analyze_performance_gaps(current_perf, baseline_perf)

        # Apply adjustments
        for adjustment in adjustments:
            param_path, change_factor = adjustment
            self._apply_parameter_adjustment(new_params, param_path, change_factor)

        return new_prompt, new_params

    def _analyze_performance_gaps(self, current_perf: PerformanceRecord,
                                 baseline_perf: Optional[PerformanceRecord]) -> List[Tuple[str, float]]:
        """
        Analyze performance gaps to determine needed adjustments.

        Args:
            current_perf: Current performance
            baseline_perf: Baseline performance

        Returns:
            List of (parameter_path, adjustment_factor) tuples
        """
        adjustments = []

        if current_perf.win_rate < 0.4:
            # Poor win rate - increase confidence thresholds
            adjustments.append(('max_confidence_threshold', 0.1))

        if current_perf.profit_factor < 1.2:
            # Poor profit factor - decrease risk per trade
            adjustments.append(('risk_per_trade', -0.05))

        # Compare to baseline if available
        if baseline_perf:
            win_rate_diff = current_perf.win_rate - baseline_perf.win_rate
            if win_rate_diff < -0.1:
                # Significantly worse win rate than baseline
                adjustments.append(('max_confidence_threshold', 0.15))

        return adjustments

    def _apply_parameter_adjustment(self, params: Dict[str, Any],
                                   param_path: str, change_factor: float):
        """
        Apply an adjustment to a parameter.

        Args:
            params: Parameter dictionary
            param_path: Dot-separated path to parameter
            change_factor: Fractional change to apply
        """
        path_parts = param_path.split('.')

        try:
            target = params
            for part in path_parts[:-1]:
                target = target[part]

            param_name = path_parts[-1]

            if isinstance(target[param_name], (int, float)):
                current_value = target[param_name]
                change = current_value * change_factor
                new_value = current_value + change

                # Apply bounds
                if 'risk' in param_name.lower() and 'max' in param_name.lower():
                    new_value = max(0.01, min(0.1, new_value))  # Risk between 1% and 10%
                elif 'confidence' in param_name.lower():
                    new_value = max(50, min(95, new_value))  # Confidence between 50% and 95%
                elif 'threshold' in param_name.lower():
                    new_value = max(60, min(90, new_value))  # Thresholds between 60% and 90%

                target[param_name] = new_value

                logger.debug(f"Adjusted {param_path}: {current_value} -> {new_value}")

        except (KeyError, TypeError) as e:
            logger.warning(f"Could not apply adjustment to {param_path}: {e}")

    def _generate_change_reason(self, current_perf: PerformanceRecord,
                               baseline_perf: Optional[PerformanceRecord]) -> str:
        """Generate a description of why the strategy was changed."""
        reasons = []

        if current_perf.win_rate < 0.4:
            reasons.append(".1f")

        if current_perf.profit_factor < 1.2:
            reasons.append(".2f")

        if baseline_perf and current_perf.win_rate < baseline_perf.win_rate:
            gap = (baseline_perf.win_rate - current_perf.win_rate) * 100
            reasons.append(f"{gap:.1f}% worse win rate than baseline")

        return "; ".join(reasons) if reasons else "Performance optimization"

    def get_performance_summary(self, version_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance summary for a strategy version.

        Args:
            version_id: Version ID to analyze (uses current if None)

        Returns:
            Dictionary containing performance metrics
        """
        version_id = version_id or self.current_version_id
        if not version_id or version_id not in self.performance_records:
            return {}

        perf = self.performance_records[version_id]
        return perf.to_dict()

    def list_strategy_versions(self) -> List[Dict[str, Any]]:
        """Get list of all strategy versions with their metadata."""
        versions = []
        for version_id, version in self.versions.items():
            version_data = version.to_dict()
            if version_id in self.performance_records:
                version_data['performance'] = self.performance_records[version_id].to_dict()
            versions.append(version_data)

        # Sort by timestamp (newest first)
        return sorted(versions, key=lambda v: v['timestamp'], reverse=True)

    def force_evolution(self, prompt_template: str = None,
                       strategy_params: Dict[str, Any] = None,
                       reason: str = "Manual override") -> str:
        """
        Force creation of a new strategy version.

        Args:
            prompt_template: New prompt template (uses current if None)
            strategy_params: New strategy params (uses current if None)
            reason: Reason for the change

        Returns:
            New version ID
        """
        current_version = self.get_strategy_version()
        if not current_version:
            raise ValueError("No current strategy version found")

        new_prompt = prompt_template or current_version.prompt_template
        new_params = strategy_params or current_version.strategy_params

        new_version_id = self.create_new_strategy_version(
            new_prompt, new_params, self.current_version_id, reason
        )

        self.current_version_id = new_version_id
        self._save_current_version()

        return new_version_id
