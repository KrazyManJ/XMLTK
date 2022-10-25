import os
from argparse import ArgumentParser

def gen_app(app_name,output_path):
    r_dir = os.path.join(os.path.abspath(output_path),app_name)
    os.makedirs(r_dir)
    open(os.path.join(r_dir,app_name+".py"),"w")\
        .write(f"import XMLTK\n\nif __name__ == '__main__':\n\tapp = XMLTK.parse('{app_name}.xml')\n\tapp.mainloop()")
    open(os.path.join(r_dir,app_name+".xml"),"w")\
        .write(f'<Tk xmlns="Tkinter" title="{app_name}">\n\n</Tk>')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-n","--name")
    parser.add_argument("-p","--path")
    args = parser.parse_args()
    if args.name is None:
        raise ValueError("You need to provide name to your project!")
    gen_app(args.name,args.path)