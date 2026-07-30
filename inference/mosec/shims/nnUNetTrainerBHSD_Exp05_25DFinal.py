"""Inference-only identity for the trainer stored in the model metadata.

The original trainer module also contains data loaders, losses, optimizers,
training loops and experiment bookkeeping. None of those are needed by
``nnUNetPredictor``. The trained model uses nnU-Net's standard network builder,
so retaining the class name on top of the base trainer is sufficient for
checkpoint discovery without shipping training functionality.
"""

from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import (
    nnUNetTrainer,
)


class nnUNetTrainerBHSD_Exp05_25DFinal(nnUNetTrainer):
    """Resolve the saved trainer name while using nnU-Net runtime behavior."""


__all__ = ["nnUNetTrainerBHSD_Exp05_25DFinal"]
