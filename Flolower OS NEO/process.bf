,                          read command

[
  -                        clear command

  >+++++[<++++++++>-]<     prepare '1'
  [                        if '1'
    >>+<<                 toggle process 1
  ]

  >+++++[<++++++++>-]<     prepare '2'
  [                        if '2'
    >>>+<<<               toggle process 2
  ]

  >+++++[<++++++++>-]<     prepare 's'
  [                        if 's'
    >>.                   print P1 state
    >>>.                  print P2 state
  ]

  ,                        next command
]
