,              read command

[
  -            clear command

  >+++++[<++++++++>-]<   prepare 'r'
  [                      if 'r' (read)
    >>.                  print cell1
    >.                   print cell2
    >.                   print cell3
    <<<                  back
  ]

  >+++++[<++++++++>-]<   prepare 'w'
  [                      if 'w' (write)
    ,                    read byte
    >>[-]<<              clear cell1
    >>+<<                write to cell1
  ]

  >+++++[<++++++++>-]<   prepare 'c'
  [                      if 'c' (clear)
    >>[-]>[-]>[-]<<<     clear 3 cells
  ]

  ,                      next command
]
