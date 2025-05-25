## 环境配置

安装所需软件并配置环境，自行安装。

## 数据集

采用公开数据集并进行筛选和手动标注，数据集地址：https://www.kaggle.com/datasets/cookiefinder/tomato-disease-multiple-sources。

**注意：**
数据集标注需转换为 YOLO 格式以用于训练，标注文件后缀为 `.txt`。

## 训练模型

### 创建配置文件

在项目根目录下创建 `data.yaml` 文件，示例内容如下（请根据实际路径和类别信息进行替换）：

```yaml
train: f:/Tomato/train/images
val: f:/Tomato/val/images
test: f:/Tomato/test/images  #此处为示例

nc: 2

# Classes
names: ['1', '2']
```
在根目录下创建`train.py` 文件，调整参数进行训练模型。
