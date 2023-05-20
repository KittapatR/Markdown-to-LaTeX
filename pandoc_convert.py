import glob
import argparse
import os
import re

parser = argparse.ArgumentParser(
    description = "Convert a markdown document into a LaTeX-generated pdf.")
parser.add_argument(
    "--filename", "-f", metavar = "-f", type = str,
    help = "put .md file to convert to pdf", nargs = "?"
)
parser.add_argument(
    "--folder", "-r", metavar="-r", type=str,
    help = "put .md folders to convert to pdf", nargs = "?"
)
parser.add_argument(
    "--xelatex", "-x", help = "Change mode of compilation, default: pdfLaTeX", action = "store_true"
)
parser.add_argument(
    "--nodate", "-nd", help = "No date compilation", action = "store_true"
)

parser.add_argument(
    "--author", "-a", type=str, help = "Add author in the LaTeX file", nargs = "?"
)

parser.add_argument(
    "--date", "-d", type=str, help = "Add date", nargs = "?"
)

parser.add_argument(
    "--hone", "-ho", help = "Header format", action = "store_true"
)

args = parser.parse_args()
if not(args.filename) and not(args.folder):
    print('Missing arguments in filename or folder.')
else:
    if (args.filename) and (args.folder):
        print("Cannot put both arguments in the same execution.")
        os._exit()
    elif args.folder:
        file_to_execute = glob.glob(r"{}/*.md".format(args.folder).replace('"', ""))
    elif args.filename:
        file_to_execute = [args.filename]
    for filename in file_to_execute:
        with open(filename, "r", encoding = "utf-8") as f:
            lines = f.readlines()
            tikz = False
            first_line = True
            new_lines = []
            for line in lines[:-1]:
                if (line.strip() == "```tikz"):
                    tikz = True
                    new_lines.append(r"\begin{center}")
                    continue
                elif (line.strip() == "```") and tikz:
                    tikz = False
                    new_lines.append(r"\end{center}")
                    continue
                elif tikz and (re.findall(r"\\usepackage|\\begin\{document\}|\\end\{document\}", line) != []):
                    continue
                if first_line:
                    if (args.author) or (args.date):
                        new_lines.append(r"\begin{center}"+"\n\n")
                        if re.findall("^#", line) != []:
                            if not(args.hone): new_lines.append(r"\textbf{" + line[1:-1] + r"}\\" + "\n")
                            else: highlight = new_lines.append(r"{\Large" + line[1:-1] + r"}\\[6pt]" + "\n")
                            
                        else:
                            new_lines.append(r"\textbf{"+"{}".format(filename[:-3].split("\\")[-1])+r"}\\"+"\n")
                        if not(args.nodate):
                            if not(args.date):
                                if (args.hone): new_lines.append(r"Last updated: \today{}\\" + "\n")
                                else: new_lines.append(r"\today{}\\" + "\n")
                            else:
                                new_lines.append(args.date+r"\\" + "\n")
                        if args.author: new_lines.append("{}  \n".format(args.author))
                        new_lines.append(r"\end{center}"+"\n\n")
                        new_lines.append("---\n")
                        if re.findall("^#", line) == []:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                    first_line = False
                else:
                    if (re.findall("[-0123456789]+", line.split(" ")[0]) != []):
                        new_lines.append(line[:-1]+"\n")
                    else: new_lines.append(line[:-1]+"  \n")
            new_lines.append(lines[-1])
        with open("{}_tmp.md".format(filename[:-3]), "w", encoding = "utf-8") as f_new:
            f_new.writelines(new_lines)
        if not(args.xelatex):
            os.system('pandoc -f markdown -t latex -V --pdf-engine=context --metadata-file=header_includes.yaml -V geometry:margin=1in -o "{}.pdf" "{}_tmp.md"'.format(filename[:-3], filename[:-3]))
        else:
            os.system('pandoc -f markdown -t latex --pdf-engine xelatex -V "mainfont:TH Sarabun Chula" -V "mainfontoptions:Scale=MatchLowercase" --metadata-file=header_includes_thai.yaml -o "{}.pdf" "{}_tmp.md"'.format(filename[:-3], filename[:-3]))
    if args.folder:
        converted = glob.glob("{}/*.pdf".format(args.folder).replace('"', ""))
    else:
        converted = ["{}.pdf".format(args.filename[:-3])]
    for pdf_file in converted:
        try:
            file_to_execute.remove(pdf_file[:-4] + ".md")
            os.remove(pdf_file[:-4] + "_tmp.md")
        except:
            continue
    print("The remaining files to convert due to LaTeX engine error:", len(file_to_execute))
    for filename in file_to_execute:
        os.system('pandoc -f markdown -t latex --pdf-engine xelatex -V "mainfont:TH Sarabun Chula" -V "mainfontoptions:Scale=MatchLowercase" --metadata-file=header_includes_thai.yaml -o "{}.pdf" "{}"'.format(filename[:-3], filename))
        os.remove(filename[:-3] + "_tmp.md")
