import torch
import torch.nn as nn
import torch.nn.functional as F

class DoubleConv(nn.Module):
    """(Conv => BN => ReLU) * 2"""
    def __init__(self, in_channels, out_channels):
        super(DoubleConv, self).__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),

            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.double_conv(x)

class UNet(nn.Module):
    def __init__(self, n_channels=3, n_classes=1):
        super(UNet, self).__init__()

        self.inc = DoubleConv(n_channels, 64)
        self.down1 = self.down_block(64, 128)
        self.down2 = self.down_block(128, 256)
        self.down3 = self.down_block(256, 512)
        self.down4 = self.down_block(512, 1024)

        self.up1 = self.up_block(1024, 512)
        self.up2 = self.up_block(512, 256)
        self.up3 = self.up_block(256, 128)
        self.up4 = self.up_block(128, 64)
        
        self.outc = nn.Conv2d(64, n_classes, kernel_size=1)

    def down_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_ch, out_ch)
        )

    def up_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.ConvTranspose2d(in_ch, out_ch, kernel_size=2, stride=2),
            DoubleConv(in_ch, out_ch)  # in_ch because we concat skip connection
        )

    def forward(self, x):
        x1 = self.inc(x)         # Encoder
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)

        x = self.up1[0](x5)      # Decoder + skip
        x = torch.cat([x, x4], dim=1)
        x = self.up1[1](x)

        x = self.up2[0](x)
        x = torch.cat([x, x3], dim=1)
        x = self.up2[1](x)

        x = self.up3[0](x)
        x = torch.cat([x, x2], dim=1)
        x = self.up3[1](x)

        x = self.up4[0](x)
        x = torch.cat([x, x1], dim=1)
        x = self.up4[1](x)

        return torch.sigmoid(self.outc(x))  # Use sigmoid for binary segmentation
