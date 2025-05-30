import torch
import torch.nn as nn
from ultralytics.nn.modules.conv import Conv


class BasicConv_FFCA(nn.Module):
    def __init__(self, in_planes, out_planes, kernel_size, stride=1, padding=0, dilation=1, groups=1, relu=True,
                 bn=True, bias=False):
        super(BasicConv_FFCA, self).__init__()
        self.out_channels = out_planes
        self.conv = nn.Conv2d(in_planes, out_planes, kernel_size=kernel_size, stride=stride, padding=padding,
                              dilation=dilation, groups=groups, bias=bias)
        self.bn = nn.BatchNorm2d(out_planes, eps=1e-5, momentum=0.01, affine=True) if bn else None
        self.relu = nn.ReLU(inplace=True) if relu else None

    def forward(self, x):
        x = self.conv(x)
        if self.bn is not None:
            x = self.bn(x)
        if self.relu is not None:
            x = self.relu(x)
        return x


class FEM(nn.Module):
    def __init__(self, in_planes, out_planes, stride=1, scale=0.1, map_reduce=8):
        super(FEM, self).__init__()
        self.scale = scale
        self.out_channels = out_planes
        inter_planes = in_planes // map_reduce
        self.branch0 = nn.Sequential(
            BasicConv_FFCA(in_planes, 2 * inter_planes, kernel_size=1, stride=stride),
            BasicConv_FFCA(2 * inter_planes, 2 * inter_planes, kernel_size=3, stride=1, padding=1, relu=False)
        )
        self.branch1 = nn.Sequential(
            BasicConv_FFCA(in_planes, inter_planes, kernel_size=1, stride=1),
            BasicConv_FFCA(inter_planes, (inter_planes // 2) * 3, kernel_size=(1, 3), stride=stride, padding=(0, 1)),
            BasicConv_FFCA((inter_planes // 2) * 3, 2 * inter_planes, kernel_size=(3, 1), stride=stride,
                           padding=(1, 0)),
            BasicConv_FFCA(2 * inter_planes, 2 * inter_planes, kernel_size=3, stride=1, padding=5, dilation=5,
                           relu=False)
        )
        self.branch2 = nn.Sequential(
            BasicConv_FFCA(in_planes, inter_planes, kernel_size=1, stride=1),
            BasicConv_FFCA(inter_planes, (inter_planes // 2) * 3, kernel_size=(3, 1), stride=stride, padding=(1, 0)),
            BasicConv_FFCA((inter_planes // 2) * 3, 2 * inter_planes, kernel_size=(1, 3), stride=stride,
                           padding=(0, 1)),
            BasicConv_FFCA(2 * inter_planes, 2 * inter_planes, kernel_size=3, stride=1, padding=5, dilation=5,
                           relu=False)
        )

        self.ConvLinear = BasicConv_FFCA(6 * inter_planes, out_planes, kernel_size=1, stride=1, relu=False)
        self.shortcut = BasicConv_FFCA(in_planes, out_planes, kernel_size=1, stride=stride, relu=False)
        self.relu = nn.ReLU(inplace=False)

    def forward(self, x):
        x0 = self.branch0(x)
        x1 = self.branch1(x)
        x2 = self.branch2(x)

        out = torch.cat((x0, x1, x2), 1)
        out = self.ConvLinear(out)
        short = self.shortcut(x)
        out = out * self.scale + short
        out = self.relu(out)

        return out