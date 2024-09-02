from pdf2image import convert_from_path
from PIL import Image
import os
from global_used_paths import poppler_path,output_folder,pdf_folder,pdf_section_folder,txt_file_dir
from PyPDF2 import PdfWriter, PdfReader

from xpinyin import Pinyin

# 使用cnocr的方案
def ocr_by_cnocr(img_path):
    from cnocr import CnOcr
    ocr = CnOcr(det_model_name='naive_det')
    out = ocr.ocr(img_path)
    out_s="".join([out_obj["text"] for out_obj in out])
    return out_s

# 使用 PaddleOCR 的 方案（这个训练效果是最好的！）
def ocr_PaddleOCR(img_path):
    from paddleocr import PaddleOCR, draw_ocr
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    out = ocr.ocr(img_path, cls=True)
    print(out)
    out_s_list=[]
    for line in out[0]:
        line_text = line[-1][0]
        print(line_text)
        out_s_list.append(line_text)
    out_s="".join(out_s_list)
    return out_s
        

def make_pdf_section(pdf_path,pdf_section_folder,section_name_pinyin,from_page_idx,to_page_idx):
    inputpdf = PdfReader(pdf_path)
    output = PdfWriter()
    my_range=range(from_page_idx,to_page_idx)

    for i in range(len(inputpdf.pages)):
        if i in my_range:
            output.add_page(inputpdf.pages[i])
    
    pdf_section_path = pdf_section_folder + os.sep + section_name_pinyin + f"{from_page_idx}-{to_page_idx}" + ".pdf"
    with open(pdf_section_path, "wb") as outputStream:
        output.write(outputStream)
    
    return pdf_section_path

def convert_pdf_to_jpg(pdf_out_path, output_folder, poppler_path,section_name_pinyin):
    images = convert_from_path(pdf_out_path, poppler_path=poppler_path)

    output_folder2=output_folder+os.sep+section_name_pinyin
    if not os.path.exists(output_folder2):
        os.makedirs(output_folder2)

    for idx, image in enumerate(images,1):
        output_filename = f"{os.path.basename(pdf_out_path).replace(".pdf","")}_{str(idx).zfill(3)}.jpg"
        output_path = os.path.join(output_folder2, output_filename)
        image.save(output_path, 'JPEG')

def main():
    for idx,file_path in enumerate(os.listdir(pdf_folder),1):
        if file_path.endswith(".pdf"):
            pdf_path = pdf_folder + os.sep + file_path
            txt_path = pdf_path.replace(".pdf",".txt")
            with open(txt_path,'r',encoding="utf-8",errors="ignore") as f:
                lines=f.readlines()
            for line in lines:
                line=line.replace("\n",'')
                section_name = line.split("**")[0]
                from_page_idx = int(line.split("**")[1].split(",")[0])-1
                to_page_idx = int(line.split("**")[1].split(",")[1])
                p = Pinyin()
                section_name_pinyin = p.get_pinyin(section_name)
                pdf_section_path = make_pdf_section(pdf_path,pdf_section_folder,section_name_pinyin,from_page_idx,to_page_idx)
                convert_pdf_to_jpg(pdf_section_path,output_folder,poppler_path,section_name_pinyin)
                out_s_list=[]
                for output_file_path in os.listdir(output_folder):
                    if output_file_path.endswith(".jpg"):
                        output_jpg_path = output_folder + os.sep + output_file_path
                        # out_s = ocr_by_cnocr(output_jpg_path)
                        out_s = ocr_PaddleOCR(output_jpg_path)
                        out_s_list.append(out_s)
                article_s="\n\n".join(out_s_list)
                with open(txt_file_dir+os.sep+section_name+".txt","w",encoding="utf-8") as f:
                    f.write(article_s)
                        # output_txt_path = output_jpg_path.replace(".jpg",".txt")
                        # with open(output_txt_path,'w',encoding="utf-8") as f:
                        #     f.write(out_s)

if __name__ == '__main__':
    main()
