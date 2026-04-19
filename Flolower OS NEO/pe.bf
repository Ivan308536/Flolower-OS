++++++++++[>+++++++>++++++++++>+++>+<<<<-]  initialize memory cells

>+++++[<++++++++++>-]<.  print 'P'
>+++++[<++++++++++>-]<.  print 'E'
>+++++[<+++++++>-]<.     print newline

,                        read input

[                        loop start
  -                      clear input (process step)

  >+++++[<++++++++++>-]<.  comment: output stage marker P
  >+++++[<++++++++++>-]<.  comment: output stage marker E
  >+++++[<+++++++>-]<.     comment: newline

  ,                      read next input
]
