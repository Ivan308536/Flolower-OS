,                read command

[
  -              clear command

  >+++++[<++++++++>-]<    prepare 'l'
  [                        if 'l'
    >++++++++[<++++++++>-]<.   print 'F'
    >+++++[<+++++++++>-]<.     print '1'
    >+++++[<+++++++>-]<.       newline

    >++++++++[<++++++++>-]<.   print 'F'
    >+++++[<+++++++++>-]<.     print '2'
    >+++++[<+++++++>-]<.       newline
  ]

  >+++++[<++++++++>-]<    prepare 'r'
  [                        if 'r'
    >>.                    print file1 byte
    <<<<.                  print file2 byte
  ]

  >+++++[<++++++++>-]<    prepare 'w'
  [                        if 'w'
    ,                      read byte
    >>[-]<<                clear file1
    >>+<<                  write to file1
  ]

  ,                        next command
]
