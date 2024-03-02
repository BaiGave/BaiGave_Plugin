

# 白给的插件

这是一个用于在Blender内直接导入模组地图、编辑Minecraft地图、将普通网格体转换为Minecraft方块，并将结果导出到存档的插件。
<!-- PROJECT SHIELDS -->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />

<p align="center">

  <h3 align="center">MC-Blender插件</h3>
  <p align="center">
    将Blender和Minecraft联系在一起
    <br />
    <a href="https://github.com/BaiGave/BaiGave_Plugin">查看Demo</a>
    ·
    <a href="https://github.com/BaiGave/BaiGave_Plugin/issues">报告Bug</a>
    ·
    <a href="https://github.com/BaiGave/BaiGave_Plugin/issues">提出新特性</a>
  </p>

</p>


 
## 目录

- [插件的基础配置](#插件的基础配置)
  - [安装插件](#安装插件)
  - [导入前准备](#导入前准备)
- [开始导入地图](#开始导入地图)
  - [导入.schem文件](#导入schem文件)
  - [导入.nbt文件](#导入nbt文件)
  - [导入存档文件](#导入存档文件)
  - [导入blockstate文件夹内的.json文件](#导入blockstae文件夹内的json文件)
- [作者](#作者)

### 插件的基础配置


###### 安装插件

请按照正常步骤安装插件

   
![1](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/d25b907a-2240-4c83-af98-d74f4d5ab42d)

（如有报错，请确定是否是下载的release里的文件，直接下载源代码会出错）



###### **导入前准备**

点击此按钮，安装原版/模组的.jar文件

![2](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/1bcabfb5-5b6d-4215-ba46-0453b0f9ea68)

资源包同理

然后此按钮可以控制优先级顺序（越上面的优先级越高）

![3](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/2640fcac-439c-4f54-9a34-222f62d36664)

和MC的这个界面类似：

![4](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/7e373066-ccfb-46fd-ae9a-b075e951faf4)



### 开始导入地图


###### 导入schem文件

(注：你可以用worldedit模组从游戏内导出.schem文件)

1.点击导入.schem文件

![5](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/413f10c9-dfea-4f42-afc0-f393e33a11b7)

2.然后会跳出二级面板，我们先按导入.schem文件

![6](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/273a2cea-0a5b-43e6-926b-a39f0797b8b4)

3.选择你的.schem文件

![7](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/d09dc514-509a-454f-a418-284630aa6236)

4.导入成功！
![8](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/ec2eee60-b4b0-4deb-b094-0deb11f51206)
(有些方块的UV可能会有问题，我们将在稍后解决)

当我们勾选了按照方块状态分离：

![9](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/3d1dbdb4-a7af-4bd0-8bb5-06a430796f14)

很好，我们成功导入了.schem文件

不过要注意的是，我的插件导入的方式和Mineways或者是jmc2obj有一些不同。

Mineways或是jmc2obj都是在外部处理好网格后，通过导入.obj文件导入进blender的。

而我的则是只导入带有blockid属性和biome属性的点云，以及所用到的方块模型进blender(每个方块状态都有一个模型在Blocks集合里)

（你可以看到它们就只是一些点罢了）

https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/1b347cb0-324b-47a6-b659-185e1c233cfb

所以我们可以做到以下操作：

方块移动：

https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/9cc36539-7890-4cef-a5ea-dc2cbf9886db

区域复制：

https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/b4f92b2a-fd6d-460f-a283-15275e693b9e

几何节点实现的延时建筑：

https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/737c2b52-0451-4318-909e-694bfef18340

几何节点实现的地形破坏：

https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/4bc00090-0fce-4a70-b23c-3b8c0dea58c2

（事实上还可以实现更多）

不过，话说回来，我们该怎么将导入进来的场景变成mineways或者jmc2obj导入进来的那种的网格体呢？

1.应用修改器

![10](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/fcabb29d-01b3-4cd0-937a-968b05589e2f)

(此过程不可逆，一旦应用，将无法实现之前的所有操作）[如果不小心应用了可以尝试crtl z 撤销大法]

2.选中需要减面的网格体，点击合并重叠面

![11](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/058b5200-9051-4d97-8a3e-427a16bfed41)

3.最后选中所有固体方块（不可以是花，藤蔓，草等方块），及UV有问题的方块

![12](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/e9f543b6-a42e-4ca0-89a4-e62f7893e0b0)

4.目前面数已经无限接近最少了，如图UV错误的玻璃窗也被修复了

![13](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/21bec841-9cdc-4272-be16-efacfdbdf9a2)

5.你可以导入Wang酱的天空预制，让你的场景变得更加好看

![14](https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/a2dabb2f-b6a2-442a-8192-97d5f65e62b1)

6.群系上色

https://github.com/BaiGave/BaiGave_Plugin/assets/107305554/ddb95008-b957-4d31-a089-51a9bcdc30a8

（通过控制biome值可以改变群系颜色）



###### 导入nbt文件

###### 导入存档文件

###### 导入blockstate文件夹内的json文件



### 作者

主要python插件开发：BaiGave(bilibili) 

多进程支持(暂时注释？)：Piggestpig(Github)/冬猫夏羊工作室(bilibili)

几何节点支持：火锅料理（bilibili） 转模部分 , 抛瓦尔第（bilibili） CTM部分（未实装) ，暗影苦力怕（面优化） ，Piggestpig(Github)/冬猫夏羊工作室(bilibili) 植物的自动摇摆，荒芜新谷（bilbil) 几种延时建筑的样式（未实装）

着色器节点支持：WangXinRui (bilbil) 动态材质（大部分借鉴） 更好的树叶半透着色器 WXR的天空预设

翻译支持：marshmallowlands (Github) 英语

### 联系方式

qq群:878232347    （有bug可以进来找白给解决)

bilibili个人主页：https://space.bilibili.com/3461563635731405?spm_id_from=333.788.0.0 （时不时会发点教程视频【虽然做的很差qwq】）


### 版权说明

该项目签署了MIT 授权许可，详情请参阅 [LICENSE.txt](https://github.com/BaiGave/BaiGave_Plugin/blob/master/LICENSE.txt)





<!-- links -->
[your-project-path]:BaiGave/BaiGave_Plugin
[contributors-shield]: https://img.shields.io/github/contributors/BaiGave/BaiGave_Plugin.svg?style=flat-square
[contributors-url]: https://github.com/BaiGave/BaiGave_Plugin/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/BaiGave/BaiGave_Plugin.svg?style=flat-square
[forks-url]: https://github.com/BaiGave/BaiGave_Plugin/network/members
[stars-shield]: https://img.shields.io/github/stars/BaiGave/BaiGave_Plugin.svg?style=flat-square
[stars-url]: https://github.com/BaiGave/BaiGave_Plugin/stargazers
[issues-shield]: https://img.shields.io/github/issues/BaiGave/BaiGave_Plugin.svg?style=flat-square
[issues-url]: https://img.shields.io/github/issues/BaiGave/BaiGave_Plugin.svg
[license-shield]: https://img.shields.io/github/license/BaiGave/BaiGave_Plugin.svg?style=flat-square
[license-url]: https://github.com/BaiGave/BaiGave_Plugin/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/shaojintian


