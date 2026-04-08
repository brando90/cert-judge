let below_zero operations =
  let rec check_balance ops balance =
    match ops with
    | [] -> false
    | x :: xs -> 
        let new_balance = balance + x in
        if new_balance < 0 then true
        else check_balance xs new_balance
  in
  check_balance operations 0;;

(* Test cases *)
let () =
  assert (below_zero [] = false);
  assert (below_zero [1; 2; -3; 1; 2; -3] = false);
  assert (below_zero [1; 2; -4; 5; 6] = true);
  assert (below_zero [1; -1; 2; -2; 5; -5; 4; -4] = false);
  assert (below_zero [1; -1; 2; -2; 5; -5; 4; -5] = true);
  assert (below_zero [1; -2; 2; -2; 5; -5; 4; -4] = true);
  
  (* Additional edge case tests *)
  assert (below_zero [-5] = true);
  assert (below_zero [5] = false);
  assert (below_zero [1; -1] = false);
  assert (below_zero [5; -3; -3] = true);
  
  print_endline "Pass!";;
