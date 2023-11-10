local a = 1
print(a)


TDBCommandType = {
    CONTINUE = 0,
    FINISH = 1,
    NEXT = 2
}

TDBBreakPointAction = {
    BP_ADD = 0,
    TBP_ADD = 1,
    DELETE = 2
}

TDBBreakPoint = {
    path = '',
    line = 0,
    addr = 0,
    enabled = false
}

TDBFilePosition = {
    path = '',
    line_number = 0,
    addr = 0,
    from = '',
    func = ''
}

TDBRequestType = {
    INFO_SOURCES = 0,
    INFO_SOURCE_FILE = 1,
    BREAKPOINTS = 2,
}

TDBResponseType = {
    UPDATE_BREAKPOINTS = 0,
    UPDATE_FILE_POSITION = 1,
}

TDBResponse = {
    header = TDBResponseType(),
    update_bks = {}
}

TDBCallBacks = {
    context = nil,
    console_output = nil,
    command_response = nil
}


print(TDBCommandType.NEXT)