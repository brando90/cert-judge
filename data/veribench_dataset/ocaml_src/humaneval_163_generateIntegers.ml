let generate_integers a b =
  let lower = max 2 (min a b) in
  let upper = min 8 (max a b) in
  if upper < lower then []
  else List.filter (fun x -> x mod 2 = 0) (List.init (upper - lower + 1) (fun i -> lower + i))

(* Test cases *)
let () =
  assert (generate_integers 2 10 = [2; 4; 6; 8]);
  assert (generate_integers 10 2 = [2; 4; 6; 8]);
  assert (generate_integers 132 2 = [2; 4; 6; 8]);
  assert (generate_integers 17 89 = []);
  assert (generate_integers 4 4 = [4]);
  assert (generate_integers 10 10 = []);
  assert (generate_integers 1 9 = [2; 4; 6; 8]);
  assert (generate_integers 0 1 = []);
  assert (generate_integers 9 12 = []);
  print_endline "Pass!";;