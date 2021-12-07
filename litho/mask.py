import matplotlib.pyplot as plt
import numpy as np
import pyfftw
import scipy.signal as sg
from PIL import Image, ImageDraw

from litho.config import PATH
from litho.gdsii.library import Library


class Mask:
    """

    Binary Mask

    Args:
        x/ymax: for the computing area
        x/y_gridsize: the simulated size of the area. Different value are supported. 2nm
        CD: used for method poly2mask, 45nm

    .. plot::
       :include-source:

        import matplotlib.pyplot as plt

        from config import PATH
        from mask import Mask

        m = Mask()
        m.x_range = [-300.0, 300.0]
        m.y_range = [-300.0, 300.0]
        m.x_gridsize = 10
        m.y_gridsize = 10
        m.openGDS(PATH.gdsdir / "AND2_X4.gds", 10)
        m.maskfft()
        m.smooth()

        plt.imshow(
            m.data,
            extent=(m.x_range[0], m.x_range[1], m.y_range[0], m.y_range[1]),
            cmap="hot",
            interpolation="none",
        )
        plt.figure()
        plt.imshow(
            m.sdata,
            extent=(m.x_range[0], m.x_range[1], m.y_range[0], m.y_range[1]),
            cmap="hot",
            interpolation="none",
        )
        plt.show()

    """

    def __init__(self, xmax=500, ymax=500, x_gridsize=1, y_gridsize=1, CD=45):
        self.x_range = [-xmax, xmax]  # nm
        self.y_range = [-ymax, ymax]
        self.x_gridsize = x_gridsize  # nm
        self.y_gridsize = y_gridsize
        self.CD = CD

    def poly2mask(self):
        """Get Pixel-based Mask Image from Polygon Data
        The Poylgon Data Form are sensitive
        Similar to poly2mask in Matlab
        """
        self.x_gridnum = int((self.x_range[1] - self.x_range[0]) / self.x_gridsize)
        self.y_gridnum = int((self.y_range[1] - self.y_range[0]) / self.y_gridsize)
        img = Image.new("L", (self.x_gridnum, self.y_gridnum), 0)

        self.perimeter = 0.0
        for ii in self.polygons:
            pp = np.array(ii) * self.CD  # polygon
            polygonlen = len(pp)
            self.perimeter += np.sum(np.abs(pp[0:-1] - pp[1:polygonlen]))
            pp[:, 0] = (pp[:, 0] - self.x_range[0]) / self.x_gridsize
            pp[:, 1] = (pp[:, 1] - self.y_range[0]) / self.y_gridsize
            vetex_list = list(pp)
            polygon = [tuple(y) for y in vetex_list]
            ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)

        self.data = np.array(img)
        self.data = np.float64(self.data)

        self.spat_part = pyfftw.empty_aligned(
            (self.y_gridnum, self.x_gridnum), dtype="complex128"
        )
        self.freq_part = pyfftw.empty_aligned(
            (self.y_gridnum, self.x_gridnum), dtype="complex128"
        )
        self.fft_mask = pyfftw.FFTW(self.spat_part, self.freq_part, axes=(0, 1))

    def openGDS(
        self,
        gdsdir,
        layer,
        boundarylayer=235,
        datatype=0,
        boundarytype=0,
        boundary=0.16,
        gdsscale=1000,
        pixels_per_um=10,
        with_fft=False,
    ):

        with open(gdsdir, "rb") as stream:
            lib = Library.load(stream)

        a = lib.pop(0)
        b = []
        xmin = []
        xmax = []
        ymin = []
        ymax = []
        for ii in range(0, len(a)):
            if a[ii].layer == layer:
                if hasattr(a[ii], "data_type"):
                    if a[ii].data_type != datatype:
                        continue
                if len(a[ii].xy) > 1:
                    aa = np.array(a[ii].xy) / gdsscale * pixels_per_um
                    b.append(aa)
                    xmin.append(min([k for k, v in aa]))
                    xmax.append(max([k for k, v in aa]))
                    ymin.append(min([v for k, v in aa]))
                    ymax.append(max([v for k, v in aa]))
        self.polylist = b
        xmin = min(xmin)
        xmax = max(xmax)
        ymin = min(ymin)
        ymax = max(ymax)

        # Use a boundary layer
        b_xmin = []
        b_xmax = []
        b_ymin = []
        b_ymax = []
        for ii in range(0, len(a)):
            if a[ii].layer == boundarylayer:
                if hasattr(a[ii], "data_type"):
                    if a[ii].data_type != boundarytype:
                        continue
                    if len(a[ii].xy) > 1:
                        aa = np.array(a[ii].xy) / gdsscale * pixels_per_um
                        b_xmin.append(min([k for k, v in aa]))
                        b_xmax.append(max([k for k, v in aa]))
                        b_ymin.append(min([v for k, v in aa]))
                        b_ymax.append(max([v for k, v in aa]))

        try:
            b_xmin = min(b_xmin)
            b_xmax = max(b_xmax)
            b_ymin = min(b_ymin)
            b_ymax = max(b_ymax)

            self.xmin = b_xmin
            self.xmax = b_xmax
            self.ymin = b_ymin
            self.ymax = b_ymax
        except ValueError:
            #print("Using percentage boundary: {}".format(boundary))
            # Use a percentage boundary
            self.xmin = xmin - boundary * (xmax - xmin)
            self.xmax = xmax + boundary * (xmax - xmin)
            self.ymin = ymin - boundary * (ymax - ymin)
            self.ymax = ymax + boundary * (ymax - ymin)
        # print(
        #     "Boundary: {0},{1} {2},{3}".format(
        #         self.xmin, self.ymin, self.xmax, self.ymax
        #     )
        # )

        self.x_range = [self.xmin, self.xmax]
        self.y_range = [self.ymin, self.ymax]

        self.x_gridnum = int((self.xmax - self.xmin) / self.x_gridsize)
        self.y_gridnum = int((self.ymax - self.ymin) / self.y_gridsize)
        img = Image.new("L", (self.x_gridnum, self.y_gridnum), 0)

        self.perimeter = 0.0
        for ii in self.polylist:
            pp = np.array(ii)  # polygon
            polygonlen = len(pp)
            self.perimeter += np.sum(np.abs(pp[0:-1] - pp[1:polygonlen]))

            pp[:, 0] = (pp[:, 0] - self.xmin) / self.x_gridsize
            pp[:, 1] = (pp[:, 1] - self.ymin) / self.y_gridsize
            vetex_list = list(pp)
            polygon = [tuple(y) for y in vetex_list]
            ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)

            self.perimeter += np.sum(np.abs(pp[0:-1] - pp[1:polygonlen]))

        self.data = np.array(img)

        # Fourier transform pair, pyfftw syntax
        self.spat_part = pyfftw.empty_aligned(
            (self.y_gridnum, self.x_gridnum), dtype="complex128"
        )
        self.freq_part = pyfftw.empty_aligned(
            (self.y_gridnum, self.x_gridnum), dtype="complex128"
        )
        self.fft_mask = pyfftw.FFTW(self.spat_part, self.freq_part, axes=(0, 1))

    # use the fftw packages
    def maskfft(self):
        self.spat_part[:] = np.fft.ifftshift(self.data)
        self.fft_mask()
        self.fdata = np.fft.fftshift(self.freq_part)

    def maskfftold(self):
        self.fdata = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(self.data)))

    def smooth(self):
        xx = np.linspace(-1, 1, 21)
        X, Y = np.meshgrid(xx, xx)
        R = X ** 2 + Y ** 2
        G = np.exp(-10 * R)
        D = sg.convolve2d(0.9 * self.data + 0.05, G, "same") / np.sum(G)
        self.sdata = D


if __name__ == "__main__":
    """polygon 2 mask"""
    # mp = [ [[-1,6],[-1, 2],[1, 2],[1, 1],[6, 1],[6, 0],[0, 0],[0, 1],[-2, 1],[-2, 6],[-1, 6]], \
    #   [[6, -1],[6, -2],[1, -2],[1, -3],[4, -3],[4, -6],[3, -6],[3, -4],[0, -4],[0, -1],[6, -1]] ]
    # m = Mask()
    # m.x_range = [-300.0,300.0]
    # m.y_range = [-300.0,300.0]
    # m.x_gridsize = 1.5
    # m.y_gridsize = 1.5
    # m.CD = 45
    # m.polygons = mp
    # m.poly2mask()

    # """from GDS"""
    m = Mask()
    # m.x_range = [-300.0, 300.0]
    # m.y_range = [-300.0, 300.0]
    m.x_gridsize = 0.25
    m.y_gridsize = 0.25
    m.openGDS(
        PATH.gdsdir / "sky130_fd_bd_sram__openram_dp_cell.gds", layer=66, datatype=20
    )
    m.maskfft()
    m.smooth()

    plt.imshow(
        m.data,
        extent=(m.x_range[0], m.x_range[1], m.y_range[0], m.y_range[1]),
        cmap="hot",
        interpolation="none",
    )
    plt.figure()
    plt.imshow(
        m.sdata,
        extent=(m.x_range[0], m.x_range[1], m.y_range[0], m.y_range[1]),
        cmap="hot",
        interpolation="none",
    )
    plt.show()
