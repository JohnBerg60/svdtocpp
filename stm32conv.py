from cmsis_svd.parser import SVDParser
import datetime
import os.path
import sys
import argparse


def fileinfo(desc):
    now = datetime.datetime.now()
    print("/*")
    print(" * John Berg @ netbasenext.nl")
    print(" *")
    print(" * %s" % (desc))
    print(" *")
    print(" * autogenerated on %s" % (now.strftime("%d.%m.%Y %H:%M")))
    print(" *")
    print(" */")
    print("")


def fileheader():
    fname, ext = os.path.splitext(__file__)
    ext = ".hpp"
    fname = os.path.join(fname + ext)
    if os.path.isfile(fname):
        with open(fname, 'r') as fin:
            print(fin.read(), end="")


def peripheralheader(peripheral):
    base = ("0x%08x" % peripheral.base_address).upper()
    result = "\n/*\n"
    result += " * %s @ %s\n" % (comment(peripheral.description), base)
    result += " */\n"
    return result


def comment(s):
    return " ".join(s.replace("\n", "").split())


def bitregister(name, fields):
    bitOffset = 0
    print("")
    print("enum class %s" % (name))
    print("{")
    for field in fields:
        if bitOffset == field.bit_offset:
            tp = ("    %s," % (field.name)).ljust(40)
        else:
            tp = ("    %s = %s," % (field.name, field.bit_offset)).ljust(40)
            bitOffset = field.bit_offset

        print("%s // %s" % (tp, comment(field.description)))
        bitOffset = bitOffset + 1
    print("};")


def run(family, mcu):
    parser = SVDParser.for_packaged_svd(family, mcu)
    device = parser.get_device()

    fileinfo(comment(device.description))
    fileheader()

    fname = "header.hpp"
    if os.path.isfile(fname):
        with open(fname, 'r') as fin:
            print(fin.read())

    for peripheral in device.peripherals:
        struct = peripheralheader(peripheral)
        base = ("0x%08x" % peripheral.base_address).upper()
        struct += "struct %s\n" % (peripheral.name)
        struct += "{\n"
        for register in peripheral.registers:
            # for now, if we have only 1 field, assume its 32 bits
            if len(register.fields) == 1:
                tp = ("    volatile uint32_t %s;" % (register.name)).ljust(40)
                struct += "%s // %s\n" % (tp, comment(register.description))
            else:  # print enum class
                enumname = "%s_%s" % (peripheral.name, register.name)
                tp = ("    reg32bit<%s> %s;" % (enumname, register.name)).ljust(40)
                struct += "%s // %s\n" % (tp, comment(register.description))
                bitregister(enumname, register.fields)

        struct += "\n"
        struct += "    void *operator new(std::size_t) {return reinterpret_cast<void *>(%s);}\n" % (base)
        struct += "};\n"
        print(struct)
        # break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SVD to C++ header converter')
    parser.add_argument('inputfile')
    parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'), help='send output to file, as a header')
    args = parser.parse_args()
    name, ext = os.path.splitext(args.inputfile)
    if ext == "":
        ext = ".svd"

    stdout = sys.stdout
    if args.outfile:
        sys.stdout = args.outfile

    run("STMicro", os.path.join(name + ext))
    sys.stdout = stdout
    print("done")
