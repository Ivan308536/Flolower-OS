++++++++++[>+++++++>++++++++++>+++>+<<<<-]
>++.                    print '>'
>,                      read input

[
  -                     clear input cell
  >++++++++[<++++++>-]  prepare 'h'
  <[                    if input == 'h'
    >++++[<++++++++>-]<.   print 'H'
    >+++++[<+++++++++>-]<. print 'E'
    >+++++[<+++++++++>-]<. print 'L'
    >+++++[<+++++++++>-]<. print 'P'
    >+++++[<+++++++>-]<.   newline
  ]

  >++++++++[<++++++>-]  prepare 'q'
  <[                    if input == 'q'
    ++++++[>++++++++<-]>++.  print 'B'
    ++++++[>++++++++<-]>+.   print 'Y'
    ++++++[>++++++++<-]>+.   print 'E'
    [-]                     exit loop
  ]

  >.                     print '>'
  ,                      read next command
]
