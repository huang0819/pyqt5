import numpy as np
import matplotlib.pyplot as plt


class RGBDData:
    def __init__(self, path):
        self.path = path

        image, depth, fx, fy = read_npz_file(path)
        self.image = image
        self.depth = depth
        self.fx = fx
        self.fy = fy


def read_npz_file(file_path):
    data = np.load(file_path)

    if 'rgb_image' in data.files and 'depth_image' in data.files:
        rgb_image = data['rgb_image']
        depth_image = data['depth_image'] * data.get('depth_scale', 1)
        fx = data.get('fx', 615.4642333984375)
        fy = data.get('fy', 615.4144897460938)

        return rgb_image, depth_image, fx, fy
    else:
        raise KeyError


class Tray:
    def __init__(self, file):
        self.file = file
        self.data = None
        self.image = None
        self.depth = None
        self.process = []

    def read_data(self):
        self.data = RGBDData(self.file)

        self.image = self.data.image[:, :, ::-1]
        self.depth = self.data.depth

    def show(self):
        fig = plt.figure(figsize=(8, 6))

        # fig.subplots_adjust(hspace=0.1, wspace=0.1)

        ax_1 = fig.add_subplot(121)
        ax_1.imshow(self.image)

        ax_2 = fig.add_subplot(122)
        ax_2.imshow(self.depth)

        plt.show()

    def preprocess(self):
        for p in self.process:
            self.depth = p['func'](self.depth, **p['param'])


if __name__ == '__main__':
    # read file
    tray = Tray(r'record/test.npz')
    tray.read_data()
    tray.show()
