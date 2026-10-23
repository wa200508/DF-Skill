"""Calibrated receive-only array math and invalid-input behavior."""
import numpy as np
import pytest
from df_skill.music import estimate_bearing,C

@pytest.mark.parametrize("angle",[-35.,20.,45.])
def test_known_bearing(angle):
    offsets=(np.arange(4)-1.5)*C/433e6/2
    rng=np.random.default_rng(120);signal=rng.normal(size=4096)+1j*rng.normal(size=4096)
    matrix=np.exp(2j*np.pi*433e6/C*offsets*np.sin(np.deg2rad(angle)))[:,None]*signal
    matrix+=1e-5*(rng.normal(size=matrix.shape)+1j*rng.normal(size=matrix.shape))
    result=estimate_bearing(matrix,offsets,433e6)
    assert result["detected"] and abs(result["angle_deg"]-angle)<.1

def test_missing_coherent_channels_fails():
    with pytest.raises(ValueError):estimate_bearing(np.ones((2,128)),[0.,.1],433e6)
