# -*- coding: utf-8 -*-
import zipfile
import os


"""压缩文件,本例以压缩nds-rom作为例子"""


def zip_file(file_absolute_path: str, zip_dir_path: str = None, zip_file_name: str = None) -> str:
    """
    压缩文件
    :param file_absolute_path: 待压缩文件/文件夹的绝对路径,
    :param zip_dir_path: 压缩文件存放的目录的绝对路径
    :param zip_file_name: 压缩文件的名称. 包含zip后缀名 xxx.zip
    :return: 压缩文件的绝对路径
    """
    if os.path.exists(file_absolute_path):
        """文件存在"""
        result = ""
        if os.path.isdir(file_absolute_path):
            """如果是目录"""
            zip_dir_path_raw, zip_file_name_raw = os.path.split(file_absolute_path)
            zip_dir_path = zip_dir_path_raw if zip_dir_path is None else zip_dir_path
            zip_file_name = "{}.zip".format(zip_file_name_raw) if zip_file_name is None else zip_file_name
            if not os.path.exists(zip_dir_path):
                os.makedirs(zip_dir_path)
            z_file_path = os.path.join(zip_dir_path, zip_file_name)
            z_file = zipfile.ZipFile(file=z_file_path, mode="w", compression=zipfile.ZIP_DEFLATED)
            for dir_path, dir_names, file_names in os.walk(top=file_absolute_path):
                    for dir_name in dir_names:
                        cur_path = os.path.join(dir_path, dir_name)
                        """使用arcname指定显示的路径"""
                        show_path = cur_path.split(file_absolute_path)[-1]
                        show_name = show_path.lstrip(os.sep)
                        z_file.write(filename=cur_path, arcname=show_name)
                    for file_name in file_names:
                        cur_path = os.path.join(dir_path, file_name)
                        """使用arcname指定显示的路径"""
                        show_path = cur_path.split(file_absolute_path)[-1]
                        show_name = show_path.lstrip(os.sep)
                        z_file.write(filename=cur_path, arcname=show_name)
            z_file.close()
            result = z_file_path
        else:
            """如果是文件"""
            zip_dir_path_raw, zip_file_name_raw_full = os.path.split(file_absolute_path)
            point_index = zip_file_name_raw_full.rfind(".")  # 点的索引位置,用于判断文件扩展名
            zip_file_name_raw = zip_file_name_raw_full[0: point_index]
            zip_dir_path = zip_dir_path_raw if zip_dir_path is None else zip_dir_path
            zip_file_name = "{}.zip".format(zip_file_name_raw) if zip_file_name is None else zip_file_name
            if not os.path.exists(zip_dir_path):
                os.makedirs(zip_dir_path)
            z_file_path = os.path.join(zip_dir_path, zip_file_name)
            z_file = zipfile.ZipFile(file=z_file_path, mode="w", compression=zipfile.ZIP_DEFLATED)
            """filename是写入文件的原始路径.arcname指定打开压缩文件时显示的路径"""
            z_file.write(filename=file_absolute_path, arcname=zip_file_name_raw_full)
            z_file.close()
            result = z_file_path
        return result
    else:
        ms = "路径:{}不存在".format(file_absolute_path)
        raise FileNotFoundError(ms)


def batch_zip(file_paths: list, zip_dir_path: str = None) -> list:
    """
    批量压缩文件,把一批文件分别压缩后,存放到zip_dir_path指定的目录,
    注意,如果出现同名文件将会被覆盖,请自行解决同名问题.
    :param file_paths: 待压缩文件绝对路径的list
    :param zip_dir_path: 压缩文件们的存放目录
    :return: 压缩文件的路径的list
    """
    if zip_dir_path is None:
        zip_dir_path = "/home/walle/ftp/pad/game/nds_zips"
    if not os.path.exists(zip_dir_path):
        os.makedirs(zip_dir_path)
    result = list()
    for file_path in file_paths:
        zip_path = zip_file(file_absolute_path=file_path, zip_dir_path=zip_dir_path)
        result.append(zip_path)
    return result


def get_nds_paths(nds_dir: str = None) -> list:
    """
    获取nds所有游戏的路径的list,
    :param nds_dir:
    :return: nds结尾的rom和其他后缀名结尾的海报,攻略的绝对路径组成的list
    """
    if nds_dir is None:
        nds_dir = "/home/walle/ftp/pad/game/NDS.Hot.Collections-3DM/nnds-roms"
    dir_paths = os.listdir(nds_dir)
    result = list()
    for name in dir_paths:
        real_path = os.path.join(nds_dir, name)
        if os.path.isdir(real_path):
            result.extend(get_nds_paths(real_path))
        else:
            result.append(real_path)
    return result


if __name__ == "__main__":
    """压缩文件"""
    # f_p = os.path.dirname(os.path.realpath(__file__))
    # zip_file(f_p)
    """获取游戏路径"""
    nds_paths = get_nds_paths()
    """压缩游戏成zip文件"""
    zip_paths = batch_zip(nds_paths)
    print(len(nds_paths), len(zip_paths))
    pass