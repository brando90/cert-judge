let has_close_elements numbers threshold =
  let rec check_pairs lst =
    match lst with
    | [] | [_] -> false
    | x :: xs ->
        List.exists (fun y -> abs_float (x -. y) < threshold) xs
        || check_pairs xs
  in
  check_pairs numbers;;

(* Test cases *)
let () =
  assert (has_close_elements [1.0; 2.0; 3.9; 4.0; 5.0; 2.2] 0.3 = true);
  assert (has_close_elements [1.0; 2.0; 3.9; 4.0; 5.0; 2.2] 0.05 = false);
  assert (has_close_elements [1.0; 2.0; 5.9; 4.0; 5.0] 0.95 = true);
  assert (has_close_elements [1.0; 2.0; 5.9; 4.0; 5.0] 0.8 = false);
  assert (has_close_elements [1.0; 2.0; 3.0; 4.0; 5.0; 2.0] 0.1 = true);
  assert (has_close_elements [1.1; 2.2; 3.1; 4.1; 5.1] 1.0 = true);
  assert (has_close_elements [1.1; 2.2; 3.1; 4.1; 5.1] 0.5 = false);
  assert (has_close_elements [] 0.1 = false);
  assert (has_close_elements [1.5] 0.1 = false);
  assert (has_close_elements [3.14; 3.14] 0.1 = true);
  assert (has_close_elements [3.14; 3.14] 0.0 = false);
  assert (has_close_elements [100.0; 200.0] 999.9 = true);
  assert (has_close_elements [1.0; 1.00000001] 1e-5 = true);
  assert (has_close_elements [1.0; 1.0002] 1e-5 = false);
  print_endline "Pass!";;
