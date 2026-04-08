let truncate_number number =
  number -. floor number;;

(* Test cases *)
let () =
  assert (truncate_number 3.5 = 0.5);
  assert (abs_float (truncate_number 1.33 -. 0.33) < 1e-6);
  assert (abs_float (truncate_number 123.456 -. 0.456) < 1e-6);
  assert (truncate_number 5.0 = 0.0);
  assert (abs_float (truncate_number 3.0000001 -. 0.0000001) < 1e-9);
  assert (abs_float (truncate_number 1234567.999999 -. 0.999999) < 1e-9);
  assert (truncate_number 0.0 = 0.0);
  print_endline "Pass!";;
