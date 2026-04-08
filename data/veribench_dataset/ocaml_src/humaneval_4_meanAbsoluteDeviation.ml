let mean_absolute_deviation numbers =
  let n = float_of_int (List.length numbers) in
  let mean = (List.fold_left ( +. ) 0.0 numbers) /. n in
  let sum_dev = List.fold_left (fun acc x -> acc +. abs_float (x -. mean)) 0.0 numbers in
  sum_dev /. n;;

(* Test cases *)
let () =
  assert (abs_float (mean_absolute_deviation [1.0; 2.0; 3.0] -. (2.0 /. 3.0)) < 1e-6);
  assert (abs_float (mean_absolute_deviation [1.0; 2.0; 3.0; 4.0] -. 1.0) < 1e-6);
  assert (abs_float (mean_absolute_deviation [1.0; 2.0; 3.0; 4.0; 5.0] -. (6.0 /. 5.0)) < 1e-6);
  
  (* Additional edge case tests *)
  assert (abs_float (mean_absolute_deviation [42.0]) < 1e-9);
  assert (abs_float (mean_absolute_deviation [5.0; 5.0; 5.0; 5.0]) < 1e-9);
  assert (abs_float (mean_absolute_deviation [10.0; 20.0; 30.0; 40.0; 50.0] -. 12.0) < 1e-6);
  let nums_small = [1.000001; 1.000002; 1.000003] in
  assert (abs_float (mean_absolute_deviation nums_small -. 0.0000006666667) < 1e-9);
  
  print_endline "Pass!";;
