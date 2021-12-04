"""
"""

import copy
import math

import numpy as np
import pyfftw
import scipy.signal as sg

from litho.image import ImageHopkins, ImageHopkinsList


class ILT:
    """inverse litho

    .. plot::
      :include-source:

        import matplotlib.pyplot as plt

        from config import PATH
        from lens import LensList
        from tcc import TCCList
        from mask import Mask
        from source import Source
        from ilt import RobustILT

        m = Mask()
        m.x_gridsize = 2.5
        m.y_gridsize = 2.5
        m.openGDS(PATH.gdsdir / "verniers.gds", layername=1, boundary=0.3)
        m.maskfft()

        s = Source()
        s.na = 1.35
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


        print("Calculating TCC and SVD kernels")
        t = TCCList(s, o)
        t.calculate()

        print("Calculating ILT")
        iterations = 2
        i = RobustILT(m, t)
        i.image.resist_a = 100
        i.image.resist_tRef = 0.9
        i.stepSize = 0.4
        i.image.doseList = [0.9, 1, 1.1]
        i.image.doseCoef = [0.3, 1, 0.3]
        i.run(iterations)

        plt.figure()
        plt.imshow(i.maskdata, origin='lower')

        plt.figure()
        plt.imshow(i.maskdata > 0.9, origin='lower')
        plt.show()

    """

    def __init__(self, m, t):
        self.image = ImageHopkins(m, t)
        self.xsize = self.image.mask.x_gridnum
        self.ysize = self.image.mask.y_gridnum
        self.error = []
        self.regMode = True
        self.regWeight = 1.0
        self.stepSize = 0.2
        self.regError = []
        self.prepare()

    def prepare(self):
        self.x1 = int(self.xsize / 2 - self.image.tcc.s.fnum)
        self.x2 = int(self.xsize / 2 + self.image.tcc.s.fnum + 1)
        self.y1 = int(self.ysize / 2 - self.image.tcc.s.gnum)
        self.y2 = int(self.ysize / 2 + self.image.tcc.s.gnum + 1)

        self.spat_part = pyfftw.empty_aligned(
            (self.image.mask.y_gridnum, self.image.mask.x_gridnum), dtype="complex128"
        )
        self.freq_part = pyfftw.empty_aligned(
            (self.image.mask.y_gridnum, self.image.mask.x_gridnum), dtype="complex128"
        )
        self.ifft_ilt = pyfftw.FFTW(
            self.freq_part, self.spat_part, axes=(0, 1), direction="FFTW_BACKWARD"
        )

        self.spat_part2 = pyfftw.empty_aligned(
            (self.image.mask.y_gridnum, self.image.mask.x_gridnum), dtype="complex128"
        )
        self.freq_part2 = pyfftw.empty_aligned(
            (self.image.mask.y_gridnum, self.image.mask.x_gridnum), dtype="complex128"
        )
        self.fft_ilt = pyfftw.FFTW(self.spat_part2, self.freq_part2, axes=(0, 1))

    def mask_init(self):
        x = np.linspace(-10, 10, 21)
        X, Y = np.meshgrid(x, x)
        R = X ** 2 + Y ** 2
        field = np.exp(-R / 2 / (4 ** 2))
        OO = field / np.sum(field)
        D = sg.fftconvolve(1.0 * self.image.mask.data + 0.0, OO, "same")
        # D = pyfftw.interfaces.scipy_fftpack.convolve(1.0*self.image.mask.data+0.0, OO,'same')

        self.target = copy.deepcopy(self.image.mask.data)
        self.maskdata = 0.99 * D + 0.01
        AA = 2 * self.maskdata - 1
        AA = np.complex64(AA)
        BB = np.arccos(AA)
        self.masktheta = BB.real

        self.image.mask.data = self.maskdata

    def calGrad(self):
        AA = (self.image.RI - self.target) * self.image.RI * (1 - self.image.RI)
        self.grad = np.zeros((self.ysize, self.xsize))

        for ii in range(self.image.order):
            e_field = np.zeros((self.ysize, self.xsize), dtype=np.complex)
            e_field[self.y1 : self.y2, self.x1 : self.x2] = (
                self.image.kernels[:, :, ii]
                * self.image.mask.fdata[self.y1 : self.y2, self.x1 : self.x2]
            )

            self.freq_part[:] = np.fft.ifftshift(e_field)
            self.ifft_ilt()
            BB = np.fft.fftshift(self.spat_part)
            # BB = np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(e_field)))
            CC = AA * BB

            self.spat_part2[:] = np.fft.ifftshift(CC)
            self.fft_ilt()
            CC_F = np.fft.fftshift(self.freq_part2)
            # CC_F = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(CC)))

            DD_F = np.conj(np.rot90(self.image.kernels[:, :, ii], 2))
            EE_F = np.zeros((self.ysize, self.xsize), dtype=np.complex)
            EE_F[self.y1 : self.y2, self.x1 : self.x2] = (
                DD_F * CC_F[self.y1 : self.y2, self.x1 : self.x2]
            )

            self.freq_part[:] = np.fft.ifftshift(EE_F)
            self.ifft_ilt()
            EE = np.fft.fftshift(self.spat_part)
            # EE = np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(EE_F)))

            FF = self.image.coefs[ii] * (EE.real)
            self.grad += np.real(FF)
        self.grad = -self.grad * np.sin(self.masktheta)

    def calRegTerm(self):
        # self.reg = np.sum(self.maskdata - self.maskdata*self.maskdata)*\
        #           (self.image.mask.x_gridsize*self.image.mask.y_gridsize/self.image.mask.perimeter)
        self.regGrad = (
            -(1 - 2 * self.maskdata)
            * np.sin(self.masktheta)
            * (
                self.image.mask.x_gridsize
                * self.image.mask.y_gridsize
                / self.image.mask.perimeter
            )
        )
        # self.regError.append(self.reg)
        # pass

    def updateThetaConstSize(self):
        if self.regMode:
            deta = self.grad + self.regWeight * self.regGrad
        else:
            deta = self.grad

        stepsize = self.stepSize / np.max(abs(deta))
        newTheta = self.masktheta - stepsize * deta

        index = newTheta > math.pi
        newTheta[index] = 2 * math.pi - newTheta[index]
        index1 = newTheta < 0
        newTheta[index1] = -newTheta[index1]
        self.masktheta = newTheta
        self.maskdata = (1 + np.cos(self.masktheta)) / 2
        self.image.mask.data = self.maskdata

    def updateThetaNormSize(self, ii):
        deta = self.grad / (self.grad.max() - self.grad.min())
        index = (deta < -0.1) + (deta > 0.1)
        newTheta = np.zeros((self.ysize, self.xsize))
        a = np.zeros((self.ysize, self.xsize))

        norm = np.sum(index)
        a[index] = 0.2 * self.error[ii] / (norm) / deta[index]
        if norm > 0:
            newTheta[index] = (
                self.masktheta[index] - 0.2 * self.error[ii] / (norm) / deta[index]
            )
            index0 = newTheta > math.pi
            newTheta[index0] = 2 * math.pi - newTheta[index0]
            index1 = newTheta < 0
            newTheta[index1] = -newTheta[index1]
        else:
            print("all zero!!")
        self.masktheta = newTheta
        self.maskdata = (1 + np.cos(self.masktheta)) / 2
        self.image.mask.data = self.maskdata
        pass

    def updateThetaWithGuide(self, ii):
        deta = self.grad
        norm = np.sum(deta * deta)
        gama = np.logspace(2, 0.1, 100) / 100
        newTheta = self.masktheta - gama[ii] * deta / norm

        index = newTheta > math.pi
        newTheta[index] = 2 * math.pi - newTheta[index]
        index1 = newTheta < 0
        newTheta[index1] = -newTheta[index1]
        self.masktheta = newTheta
        self.maskdata = (1 + np.cos(self.masktheta)) / 2
        self.image.mask.data = self.maskdata
        pass

    def run(self, num=10):
        self.mask_init()
        for ii in range(num):
            self.image.mask.maskfft()
            self.image.calAI()
            self.image.calRI()
            self.costfunction()
            self.calGrad()
            self.calRegTerm()
            self.updateThetaConstSize()
            print(ii)

    def keepon(self, num=10):
        for ii in range(num):
            self.image.mask.maskfft()
            self.image.calAI()
            self.image.calRI()
            self.costfunction()
            self.calGrad()
            self.calRegTerm()
            self.updateThetaConstSize()
            print(ii)

    def costfunction(self):
        a = np.sum((self.image.RI - self.target) ** 2) * (
            self.image.mask.x_gridsize
            * self.image.mask.y_gridsize
            / self.image.mask.perimeter
        )
        self.error.append(a)


class RobustILT(ILT):
    def __init__(self, mask, tccList):
        self.image = ImageHopkinsList(mask, tccList)
        self.xsize = self.image.mask.x_gridnum
        self.ysize = self.image.mask.y_gridnum
        self.mask_init()
        self.error = []
        self.regMode = False
        self.prepare()

    def calRobustGrad(self):
        length = len(self.image.focusList)
        lengthD = len(self.image.doseList)
        self.robustGrad = np.zeros((self.ysize, self.xsize))
        for ii in range(length):
            self.image.kernels = self.image.kernelList[ii]
            self.image.coefs = self.image.coefList[ii]
            for jj in range(lengthD):
                self.image.RI = self.image.RIList[ii][jj]
                self.calGrad()
                self.robustGrad += (
                    self.image.doseCoef[jj] * self.image.focusCoef[ii] * self.grad
                )
        self.grad = self.robustGrad

    def robustCostFunction(self):
        length = len(self.image.focusList)
        lengthD = len(self.image.doseList)
        norm = np.sum(self.image.doseCoef) * np.sum(self.image.focusCoef)
        ra = 0.0
        for ii in range(length):
            for jj in range(lengthD):
                a = np.sum((self.image.RIList[ii][jj] - self.target) ** 2) * (
                    self.image.mask.x_gridsize
                    * self.image.mask.y_gridsize
                    / self.image.mask.perimeter
                )
                ra += self.image.doseCoef[jj] * self.image.focusCoef[ii] * a
        self.error.append(ra / norm)

    def run(self, num=10):
        for ii in range(num):
            self.image.mask.maskfft()
            self.image.AIList = []
            self.image.RIList = []
            self.image.calculate()
            self.robustCostFunction()
            self.calRobustGrad()
            # self.calGrad()
            self.calRegTerm()
            self.updateThetaConstSize()
            print(
                "Interation index: %d, Costfunction value: %4f."
                % (
                    ii,
                    self.error[ii],
                )
            )


if __name__ == "__main__":

    import time

    from config import PATH
    from lens import LensList
    from mask import Mask
    from source import Source
    from tcc import TCCList

    a = time.time()
    m = Mask()
    m.x_range = [-300.0, 300.0]
    m.y_range = [-300.0, 300.0]
    m.x_gridsize = 2.5
    m.y_gridsize = 2.5
    m.openGDS(PATH.gdsdir / "NOR2_X2.gds", 11, 0.3)
    m.maskfft()

    s = Source()
    s.na = 1.35
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
    o.focusList = [0, 80]
    o.focusCoef = [1, 0.5]
    o.calculate()

    print("Calculating TCC and SVD kernels")
    t = TCCList(s, o)
    t.calculate()

    print("Calculating ILT")
    i = RobustILT(m, t)
    i.image.resist_a = 100
    i.image.resist_tRef = 0.6
    i.stepSize = 0.4
    i.image.doseList = [0.9, 1, 1.1]
    i.image.doseCoef = [0.3, 1, 0.3]
    i.run(2)

    a = np.array(i.error)
    b = (a[0:-2] - a[1:-1]) / a[0:-2]


#    s = Source()
#    s.na = 1.25
#    s.maskxpitch = 600.0
#    s.maskypitch = 1000.0
#    s.type = 'annular'
#    s.sigma_in = 0.5
#    s.sigma_out = 0.8
#    s.update()
#    s.ifft()
#
#    o = Lens()
#    o.na = s.na
#    o.maskxpitch = 600.0
#    o.maskypitch = 1000.0
#    o.update()
#    o.calPupil()
#    o.calPSF()
#
#    t = TCC(s,o)
#    t.calMutualIntensity()
#    t.calSpatTCC()
#    t.svd()
#
#
#    ilt = ILT(m,t)
#    ilt.image.resist_a = 100
#    ilt.mask_init()
#    ilt.run(100)
