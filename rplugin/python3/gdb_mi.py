
if __name__ == '__main__':
    ins = GDBInstance()
    ins.start()
    output = ins.execute(GDBCommand("print 1"))
    print(output.get_msg())
    print(output.get_console_msg())
    print(output.get_total_msg())
    output = ins.execute(GDBCommand("print 1+1"))
    print(output.get_msg())
    print(output.get_console_msg())
    print(output.get_total_msg())
    ins.exit()

