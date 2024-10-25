    @PY_EMBED_TEMPLATE_FILES@

    import os, sys
    argv = sys.argv[1:]

    try:
        library_name = argv[0].replace('-', '_')
        cpp_path = argv[1]
        h_path = argv[2]
        gdext_path = argv[3]
    except:
        print(
            '',
            'ERROR: Not enough arguments.',
            'Needed arguments (<argument> - example):',
            '',
            '<library_name>              (`my_library_name`)',
            '<cpp_file_path>             (`src/register_types.cpp`)',
            '<header_file_path>          (`include/register_types.h`)',
            '<gdextension_file_path>     (`project/my_library.gdextension`)',
            '',
	        sep='\n', file=sys.stderr)
        exit(1)

    print(
        'These files will be affected:',
        f'{"(New)     " if not os.path.exists(gdext_path) else "(Override)"} {gdext_path}',
        f'{"(New)     " if not os.path.exists(cpp_path) else "(Override)"} {cpp_path}',
        f'{"(New)     " if not os.path.exists(h_path) else "(Override)"} {h_path}',
        sep='\n')
    while True:
        inp = input('Are you sure? (Y/N) ')
        if inp == '':
            continue
        if inp not in 'yY':
            print('No changes, exiting...')
            exit(1)
        break

    print(f"Configuring '{gdext_path}' ...")
    open(gdext_path, 'w').write(
        SCRIPTS_GDEXTENSION_IN.replace('@LIBRARY_NAME@', library_name))

    print(f"Configuring '{cpp_path}' ...")
    open(cpp_path, 'w').write(
        REGISTER_TYPES_CPP_IN.replace('@LIBRARY_NAME@', library_name))

    print(f"Configuring '{h_path}' ...")
    open(h_path, 'w').write(
        REGISTER_TYPES_H_IN.replace('@LIBRARY_NAME@', library_name))

    print("Files configured.")
    exit(0)
