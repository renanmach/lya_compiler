  H = ["Welcome.\n", "What’s you name?", "Nice to meet you "]
  [
   (’stp’),
   (’alc’, 11),
   (’ldc’, 0),
   (’stv’, 0, 0),    # dcl name chars[10];
   (’prc’, 0),      # print("Welcome.\n");
   (’prc’, 1),      # print("What’s your name?");
   (’ldr’, 0, 0),
   (’rds’),         # read(name);
   (’prc’, 2),
   (’ldr’, 0, 0),
   (’prs’),         # print("Nice to meet you ", name);
   (’dlc’, 11),
   (’end’)
  ]