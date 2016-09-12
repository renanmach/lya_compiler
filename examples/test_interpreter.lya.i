  [
   (’stp’),
   (’alc’, 2),      # dcl i,k int;
   (’rdv’),
   (’stv’, 0, 1),   # read(k);
   (’ldc’, 1),
   (’stv’, 0, 0),   # i=1;
   (’lbl’, 1),      # do
   (’ldv’, 0, 0),
   (’ldv’, 0, 1),
   (’leq’),
   (’jof’, 2),      #   while i<=k;
   (’ldv’, 0, 0),
   (’ldv’, 0, 0),
   (’mul’),
   (’prv’),         #      print(i*i);
   (’ldv’, 0, 0),
   (’ldc’, 1),
   (’add’),
   (’stv’, 0, 0),   #      i=i+1;
   (’jmp’, 1),      # od;
   (’lbl’, 2),
   (’dlc’, 2),
   (’end’)
  ]