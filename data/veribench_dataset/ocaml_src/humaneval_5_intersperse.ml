let intersperse numbers delimiter =
  let rec aux acc = function
    | [] -> acc
    | [x] -> x :: acc
    | x :: xs -> aux (delimiter :: x :: acc) xs
  in
  List.rev (aux [] numbers);;

(* Test cases *)
let () =
  assert (intersperse [] 7 = []);
  assert (intersperse [5; 6; 3; 2] 8 = [5; 8; 6; 8; 3; 8; 2]);
  assert (intersperse [2; 2; 2] 2 = [2; 2; 2; 2; 2]);
  
  (* Additional edge case tests *)
  assert (intersperse [42] 9 = [42]);
  assert (intersperse [1; 2] (-1) = [1; -1; 2]);
  
  (* Large list test *)
  let big_input = [1; 2; 3; 4; 5] in
  let big_output = intersperse big_input 0 in
  assert (List.length big_output = 2 * List.length big_input - 1);
  
  (* Checking correct pattern *)
  let rec check_pattern lst orig del =
    match lst, orig with
    | [], [] -> true
    | [x], [y] -> x = y
    | x :: d :: xs, y :: ys -> x = y && d = del && check_pattern xs ys del
    | _, _ -> false
  in
  assert (check_pattern big_output big_input 0);
  
  print_endline "Pass!";;
