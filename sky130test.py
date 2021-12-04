"""
Created on Wen Apr 27 2016
@author: WenLv (wenlv@hust.edu.cn)
"""
import time

import matplotlib.pyplot as plt
from litho.config import PATH
from litho.ilt import ILT
from litho.lens import LensList
from litho.mask import Mask
from litho.source import Source
from litho.tcc import TCCList


def test_inverse_litho():
    m = Mask()
    m.x_gridsize = 0.025
    m.y_gridsize = 0.025

    if 0:
        NA = 1.35
        gdspath = PATH.gdsdir / "NOR2_X2.gds"
        # M1
        m.openGDS(gdspath, layer=11, boundary=0.3, gdsscale=10000)
        # contact
        # m.openGDS(gdspath, layer=10, boundary=0.3, gdsscale=100)
    else:
        NA = 0.69
        m.CD = 130
        # gdspath = PATH.sky130gdsdir / "sky130_fd_bd_sram__openram_dp_cell.gds"
        gdspath = PATH.sky130gdsdir / "sky130_bitcell_array_flat.gds"
        # gdspath = PATH.sky130gdsdir / "sky130_bitcell_array_OPC.gds"
        # diff
        # m.openGDS(gdspath, layer=65, boundarytype=4, datatype=20, boundary=0, gdsscale=10000)
        # poly
        m.openGDS(
            gdspath, layer=66, boundarytype=4, datatype=20, boundary=0, gdsscale=10000
        )
        # LI
        # m.openGDS(gdspath, layer=67, boundarytype=4, datatype=20, boundary=0, gdsscale=10000)
        # mcon
        # m.openGDS(gdspath, layer=67, datatype=44, boundary=0, gdsscale=1000)
        # M1
        # m.openGDS(gdspath, layer=68, datatype=20, boundary=0, gdsscale=1000)

    m.maskfft()

    x, y, dx, dy = (0, 0, 640, 550)
    plt.figure()
    mngr = plt.get_current_fig_manager()
    mngr.window.setGeometry(x, y, dx, dy)
    x += dx
    plt.imshow(
        m.data,
        cmap="hot",
        interpolation="none",
    )

    if 1:
        m.smooth()

        plt.figure()
        mngr = plt.get_current_fig_manager()
        mngr.window.setGeometry(x, y, dx, dy)
        x += dx
        plt.imshow(
            m.sdata,
            cmap="hot",
            interpolation="none",
        )

    s = Source()
    s.na = NA
    s.maskxpitch = m.x_range[1] - m.x_range[0]
    s.maskypitch = m.y_range[1] - m.y_range[0]
    s.type = "annular"
    s.sigma_in = 0.7
    s.sigma_out = 0.9
    s.smooth_deta = 0.00
    s.shiftAngle = 0
    s.update()
    s.ifft()

    o = LensList()
    o.na = s.na
    o.maskxpitch = s.maskxpitch
    o.maskypitch = s.maskypitch
    o.focusList = [0]
    o.focusCoef = [1]
    o.calculate()

    tic = time.time()
    print("Calculating TCC and SVD kernels")
    t = TCCList(s, o)
    t.calculate()
    print("###taking %1.3f seconds" % (time.time() - tic))

    print("Calculating ILT")
    # i = RobustILT(m, t)
    i = ILT(m, t)
    i.image.resist_a = 100
    i.image.resist_tRef = 0.9
    i.stepSize = 0.4
    i.image.doseList = [0.9, 1, 1.1]
    i.image.doseCoef = [0.3, 1, 0.3]
    i.run(10)

    # ILT Mask for sim
    m2 = Mask()
    m2.x_gridsize = 0.025
    m2.y_gridsize = 0.025
    m2.data = i.maskdata > 0.9
    m2.smooth()

    plt.figure()
    mngr = plt.get_current_fig_manager()
    mngr.window.setGeometry(x, y, dx, dy)
    x += dx
    plt.imshow(m2.data > 0.9)

    plt.figure()
    mngr = plt.get_current_fig_manager()
    mngr.window.setGeometry(x, y, dx, dy)
    x += dx
    plt.imshow(
        m2.sdata,
        cmap="hot",
        interpolation="none",
    )

    plt.show()


if __name__ == "__main__":
    test_inverse_litho()
