import os
import shutil
import asyncio
import img2pdf
import jmcomic

from PIL import Image

from astrbot.api.star import Star, Context
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.message_components import File


MAX_PDF_SIZE = 45 * 1024 * 1024


class JMComicDownloadPlugin(Star):

    def __init__(self, context: Context):
        super().__init__(context)

        config_path = os.path.join(
            os.path.dirname(__file__),
            "config.yml"
        )

        self.option = jmcomic.create_option_by_file(
            config_path
        )

        plugin_dir = os.path.dirname(__file__)

        self.download_dir = os.path.join(
            plugin_dir,
            "downloads"
        )

        os.makedirs(
            self.download_dir,
            exist_ok=True
        )

        self.option.dir_rule.base_dir = self.download_dir

        self.client = self.option.build_jm_client()

        self.download_lock = asyncio.Lock()


    def find_image_folder(self, aid):

        aid_dir = os.path.join(
            self.download_dir,
            str(aid)
        )

        for root, dirs, files in os.walk(aid_dir):

            for file in files:

                if file.lower().endswith(
                    (".webp", ".jpg", ".jpeg", ".png")
                ):
                    return root

        return None



    def images_to_pdf(self, folder, output_prefix):

        images = []

        temp_dir = os.path.join(
            folder,
            "converted"
        )

        os.makedirs(
            temp_dir,
            exist_ok=True
        )


        for file in sorted(os.listdir(folder)):

            file_path = os.path.join(
                folder,
                file
            )


            if file.lower().endswith(".webp"):

                jpg_path = os.path.join(
                    temp_dir,
                    file.rsplit(".", 1)[0] + ".jpg"
                )


                img = Image.open(
                    file_path
                ).convert(
                    "RGB"
                )


                img.save(
                    jpg_path,
                    "JPEG"
                )


                images.append(
                    jpg_path
                )


            elif file.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):

                images.append(
                    file_path
                )


        if not images:

            raise Exception(
                "没有找到图片"
            )


        pdf_files = []

        current_images = []

        part = 1


        for image in images:

            current_images.append(
                image
            )


            temp_pdf = os.path.join(
                self.download_dir,
                f"{output_prefix}_{part}.pdf"
            )


            with open(temp_pdf, "wb") as f:

                f.write(
                    img2pdf.convert(
                        current_images
                    )
                )


            if os.path.getsize(temp_pdf) > MAX_PDF_SIZE:


                os.remove(
                    temp_pdf
                )


                if len(current_images) == 1:

                    raise Exception(
                        "单页图片过大，无法生成PDF"
                    )


                last_images = current_images[:-1]


                with open(temp_pdf, "wb") as f:

                    f.write(
                        img2pdf.convert(
                            last_images
                        )
                    )


                pdf_files.append(
                    temp_pdf
                )


                part += 1


                current_images = [
                    image
                ]


        if current_images:

            final_pdf = os.path.join(
                self.download_dir,
                f"{output_prefix}_{part}.pdf"
            )


            with open(final_pdf, "wb") as f:

                f.write(
                    img2pdf.convert(
                        current_images
                    )
                )


            pdf_files.append(
                final_pdf
            )


        return pdf_files



    def clean_download(self, aid):


        for file in os.listdir(
            self.download_dir
        ):

            if (
                file.startswith(str(aid))
                and file.endswith(".pdf")
            ):

                os.remove(
                    os.path.join(
                        self.download_dir,
                        file
                    )
                )


        comic_dir = os.path.join(
            self.download_dir,
            str(aid)
        )


        if os.path.exists(
            comic_dir
        ):

            shutil.rmtree(
                comic_dir
            )



    @filter.command("jmhelp")
    async def jmhelp(
        self,
        event: AstrMessageEvent
    ):

        yield event.plain_result(
            "JMComic 下载插件帮助\n\n"
            "查询作品：\n"
            "/jm <ID>\n\n"
            "下载作品：\n"
            "/jmd <ID>\n\n"
            "示例：\n"
            "/jm 350234\n"
            "/jmd 350234\n\n"
            "下载完成后自动转换PDF并清理缓存。"
        )



    @filter.command("jm")
    async def jm(
        self,
        event: AstrMessageEvent,
        aid: str
    ):


        try:

            aid = int(aid)


            album = self.client.get_album_detail(
                aid
            )


            yield event.plain_result(
                f"标题：{album.name}\n"
                f"作者：{album.author}\n"
                f"ID：{album.id}"
            )


        except Exception as e:

            yield event.plain_result(
                f"查询失败：{e}"
            )



    @filter.command("jmd")
    async def jmd(
        self,
        event: AstrMessageEvent,
        aid: str
    ):


        try:

            aid = int(aid)


            if self.download_lock.locked():

                yield event.plain_result(
                    "当前有任务正在下载，请稍后再试"
                )

                return



            async with self.download_lock:


                yield event.plain_result(
                    "开始下载..."
                )


                self.option.download_album(
                    aid
                )


                yield event.plain_result(
                    "下载完成，正在生成PDF..."
                )



                image_folder = self.find_image_folder(
                    aid
                )


                if image_folder is None:

                    raise Exception(
                        "找不到图片目录"
                    )



                pdf_files = self.images_to_pdf(
                    image_folder,
                    str(aid)
                )



                yield event.plain_result(
                    f"PDF生成完成，共{len(pdf_files)}个文件，正在发送..."
                )



                try:

                    for pdf in pdf_files:

                        yield event.chain_result(
                            [
                                File(
                                    name=os.path.basename(pdf),
                                    file=pdf
                                )
                            ]
                        )


                finally:

                    self.clean_download(
                        aid
                    )


        except Exception as e:

            yield event.plain_result(
                f"下载失败：{e}"
            )